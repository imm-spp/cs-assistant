from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.llm import LLMError, get_llm
from app.llm.fake import FakeProvider
from app.main import app
from app.models import Customer
from app.services.draft import DRAFT_SYSTEM_PROMPT, build_draft_prompt


class FailingProvider(FakeProvider):
    def chat(self, system: str, user: str) -> str:
        raise LLMError("ต่อ Ollama ไม่ได้")


@pytest.fixture
def fake_llm() -> Iterator[FakeProvider]:
    llm = FakeProvider(reply="\n เรียน คุณสมชาย ... ทีมดูแลลูกค้า \n")
    app.dependency_overrides[get_llm] = lambda: llm
    yield llm


def add_customer(session: Session) -> Customer:
    customer = Customer(
        name="Somchai Test",
        email="somchai@example.com",
        phone="000",
        company="Acme",
        tier="premium",
        notes="ชำระเงินล่าช้า 15 วัน",
    )
    session.add(customer)
    session.commit()
    session.refresh(customer)
    return customer


@pytest.mark.parametrize(("language", "label"), [("th", "ภาษาไทย"), ("en", "English")])
def test_prompt_includes_instruction_and_language(language: str, label: str) -> None:
    customer = Customer(name="Alice Mock", email="a@example.com", phone="1", company="Globex")

    prompt = build_draft_prompt(customer, "ทวงค่าบริการอย่างสุภาพ", language)  # type: ignore[arg-type]

    assert "Alice Mock" in prompt
    assert "ทวงค่าบริการอย่างสุภาพ" in prompt
    assert f"ภาษาที่ต้องใช้: {label}" in prompt


def test_draft_endpoint_returns_llm_reply(
    client: TestClient, session: Session, fake_llm: FakeProvider
) -> None:
    customer = add_customer(session)

    response = client.post(
        f"/api/ai/customers/{customer.id}/draft",
        json={"instruction": "ตามเรื่องค่าบริการค้างชำระ", "language": "th"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "customer_id": customer.id,
        "language": "th",
        "draft": "เรียน คุณสมชาย ... ทีมดูแลลูกค้า",
    }
    system, user = fake_llm.calls[0]
    assert system == DRAFT_SYSTEM_PROMPT
    assert "ตามเรื่องค่าบริการค้างชำระ" in user
    assert "ชำระเงินล่าช้า 15 วัน" in user


def test_draft_defaults_to_thai(
    client: TestClient, session: Session, fake_llm: FakeProvider
) -> None:
    customer = add_customer(session)

    response = client.post(f"/api/ai/customers/{customer.id}/draft", json={"instruction": "hi"})

    assert response.json()["language"] == "th"


@pytest.mark.parametrize(
    "body",
    [
        {"instruction": "", "language": "th"},
        {"instruction": "   ", "language": "th"},
        {"instruction": "hi", "language": "jp"},
        {"language": "en"},
    ],
)
def test_draft_rejects_invalid_body(
    client: TestClient, session: Session, fake_llm: FakeProvider, body: dict[str, str]
) -> None:
    customer = add_customer(session)

    response = client.post(f"/api/ai/customers/{customer.id}/draft", json=body)

    assert response.status_code == 422
    assert fake_llm.calls == []


def test_draft_missing_customer_returns_404(client: TestClient, fake_llm: FakeProvider) -> None:
    response = client.post("/api/ai/customers/9999/draft", json={"instruction": "hi"})

    assert response.status_code == 404


def test_draft_llm_error_returns_502(client: TestClient, session: Session) -> None:
    customer = add_customer(session)
    app.dependency_overrides[get_llm] = lambda: FailingProvider()

    response = client.post(f"/api/ai/customers/{customer.id}/draft", json={"instruction": "hi"})

    assert response.status_code == 502


def test_prompt_only_includes_greeting_rules_for_chosen_language() -> None:
    customer = Customer(name="Alice Mock", email="a@example.com", phone="1", company="Globex")

    thai = build_draft_prompt(customer, "hi", "th")
    english = build_draft_prompt(customer, "hi", "en")

    assert "เรียน คุณAlice Mock" in thai and "Dear" not in thai
    assert "Dear Alice Mock," in english and "ทีมดูแลลูกค้า" not in english
