from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.llm import LLMError, get_llm
from app.llm.fake import FakeProvider
from app.main import app
from app.models import Customer
from app.services.summary import SUMMARY_SYSTEM_PROMPT, build_customer_prompt


class FailingProvider(FakeProvider):
    def chat(self, system: str, user: str) -> str:
        raise LLMError("ต่อ Ollama ไม่ได้")


@pytest.fixture
def fake_llm() -> Iterator[FakeProvider]:
    llm = FakeProvider(reply="  - ลูกค้า enterprise ควรดูแลพิเศษ  ")
    app.dependency_overrides[get_llm] = lambda: llm
    yield llm
    # client fixture จะล้าง dependency_overrides ทั้งหมดให้ตอนจบ


def add_customer(session: Session) -> Customer:
    customer = Customer(
        name="Somchai Test",
        email="somchai@example.com",
        phone="000",
        company="Acme",
        tier="enterprise",
        notes="ขอใบเสนอราคาใหม่",
    )
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


def test_prompt_includes_customer_details() -> None:
    customer = Customer(
        name="Alice Mock", email="a@example.com", phone="111", company="Globex", tier="premium"
    )

    prompt = build_customer_prompt(customer)

    for text in ["Alice Mock", "Globex", "a@example.com", "premium", "(ไม่มี)"]:
        assert text in prompt


def test_summary_endpoint_returns_llm_reply(
    client: TestClient, session: Session, fake_llm: FakeProvider
) -> None:
    customer = add_customer(session)

    response = client.post(f"/api/ai/customers/{customer.id}/summary")

    assert response.status_code == 200
    assert response.json() == {
        "customer_id": customer.id,
        "summary": "- ลูกค้า enterprise ควรดูแลพิเศษ",
    }
    system, user = fake_llm.calls[0]
    assert system == SUMMARY_SYSTEM_PROMPT
    assert "Somchai Test" in user
    assert "ขอใบเสนอราคาใหม่" in user


def test_summary_missing_customer_returns_404(client: TestClient, fake_llm: FakeProvider) -> None:
    response = client.post("/api/ai/customers/9999/summary")

    assert response.status_code == 404
    assert fake_llm.calls == []


def test_summary_llm_error_returns_502(client: TestClient, session: Session) -> None:
    customer = add_customer(session)
    app.dependency_overrides[get_llm] = lambda: FailingProvider()

    response = client.post(f"/api/ai/customers/{customer.id}/summary")

    assert response.status_code == 502
    assert "Ollama" in response.json()["detail"]
