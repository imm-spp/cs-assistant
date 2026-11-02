from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.llm import LLMError, get_llm
from app.llm.fake import FakeProvider
from app.main import app
from app.rag.embedding import FakeEmbedder, get_embedder
from app.rag.ingest import ingest_documents
from app.rag.retrieval import search_chunks
from app.services.qa import (
    MIN_SCORE,
    NO_DOCUMENTS_ANSWER,
    NOT_FOUND_ANSWER,
    QA_SYSTEM_PROMPT,
    build_qa_prompt,
)

# FakeEmbedder จับคู่จากคำที่เหมือนกัน จึงใช้คำภาษาอังกฤษแยกชัด ๆ ในเอกสารทดสอบ
DOCS = {
    "pricing.md": "# Pricing\n\n## Plans\nstandard plan costs 290 baht per user",
    "login.md": "# Login\n\n## Password\nreset password link expires after 30 minutes",
    "billing.md": "# Billing\n\n## Invoice\ninvoice is issued on the first day of month",
}


@pytest.fixture
def docs_dir(tmp_path: Path) -> Path:
    for name, text in DOCS.items():
        (tmp_path / name).write_text(text, encoding="utf-8")
    return tmp_path


@pytest.fixture
def fake_llm() -> Iterator[FakeProvider]:
    llm = FakeProvider(reply=" ลิงก์ใช้ได้ 30 นาที (ที่มา: login.md) ")
    app.dependency_overrides[get_llm] = lambda: llm
    app.dependency_overrides[get_embedder] = FakeEmbedder
    yield llm


def test_search_returns_most_similar_chunk_first(session: Session, docs_dir: Path) -> None:
    ingest_documents(session, FakeEmbedder(), docs_dir)

    results = search_chunks(session, FakeEmbedder(), "password reset link", top_k=2)

    assert len(results) == 2
    assert results[0].source == "login.md"
    assert results[0].score > results[1].score


def test_ask_returns_answer_and_sources(
    client: TestClient, session: Session, docs_dir: Path, fake_llm: FakeProvider
) -> None:
    ingest_documents(session, FakeEmbedder(), docs_dir)

    response = client.post("/api/rag/ask", json={"question": "password reset link expires?"})

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "ลิงก์ใช้ได้ 30 นาที (ที่มา: login.md)"
    assert data["sources"][0]["source"] == "login.md"
    assert "30 minutes" in data["sources"][0]["content"]

    system, user = fake_llm.calls[0]
    assert system == QA_SYSTEM_PROMPT
    assert "[เอกสาร 1: login.md]" in user
    assert "คำถาม: password reset link expires?" in user
    assert "ตอบเป็นภาษา: English" in user
    # ส่งให้ LLM เฉพาะชิ้นที่คะแนนผ่านเกณฑ์
    assert all(source["score"] >= MIN_SCORE for source in data["sources"])


def test_ask_unrelated_question_skips_llm(
    client: TestClient, session: Session, docs_dir: Path, fake_llm: FakeProvider
) -> None:
    ingest_documents(session, FakeEmbedder(), docs_dir)

    response = client.post("/api/rag/ask", json={"question": "tom yum soup recipe"})

    assert response.json() == {"answer": NOT_FOUND_ANSWER, "sources": []}
    assert fake_llm.calls == []


@pytest.mark.parametrize(
    ("question", "language"),
    [("ลืมรหัสผ่านทำยังไง", "ภาษาไทย"), ("How do I reset it?", "English")],
)
def test_qa_prompt_tells_model_which_language(question: str, language: str) -> None:
    assert f"ตอบเป็นภาษา: {language}" in build_qa_prompt(question, [])


def test_ask_without_documents_does_not_call_llm(
    client: TestClient, fake_llm: FakeProvider
) -> None:
    response = client.post("/api/rag/ask", json={"question": "anything"})

    assert response.json() == {"answer": NO_DOCUMENTS_ANSWER, "sources": []}
    assert fake_llm.calls == []


@pytest.mark.parametrize("body", [{"question": ""}, {"question": "   "}, {}])
def test_ask_rejects_blank_question(
    client: TestClient, fake_llm: FakeProvider, body: dict[str, str]
) -> None:
    response = client.post("/api/rag/ask", json=body)

    assert response.status_code == 422


def test_ask_llm_error_returns_502(
    client: TestClient, session: Session, docs_dir: Path, fake_llm: FakeProvider
) -> None:
    ingest_documents(session, FakeEmbedder(), docs_dir)

    class FailingProvider(FakeProvider):
        def chat(self, system: str, user: str) -> str:
            raise LLMError("ต่อ Ollama ไม่ได้")

    app.dependency_overrides[get_llm] = lambda: FailingProvider()

    response = client.post("/api/rag/ask", json={"question": "invoice"})

    assert response.status_code == 502
