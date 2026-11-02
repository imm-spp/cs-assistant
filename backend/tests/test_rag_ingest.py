import json
from pathlib import Path
from typing import Any

import httpx
import pytest
from sqlmodel import Session, select

from app.llm import LLMError
from app.models import DocumentChunk
from app.rag.chunking import chunk_document, split_long_text
from app.rag.embedding import EMBEDDING_DIM, FakeEmbedder, OllamaEmbedder
from app.rag.ingest import DOCS_DIR, ingest_documents, load_chunks

SAMPLE_DOC = """# คู่มือทดสอบ

บทนำสั้น ๆ

## หัวข้อแรก
เนื้อหาหัวข้อแรก

## หัวข้อสอง
เนื้อหาหัวข้อสอง
"""

# ---------- chunking ----------


def test_chunk_document_splits_by_heading_and_adds_title() -> None:
    chunks = chunk_document("guide.md", SAMPLE_DOC)

    assert [chunk.index for chunk in chunks] == [0, 1, 2]
    assert chunks[0].content == "คู่มือทดสอบ\nบทนำสั้น ๆ"
    assert chunks[1].content == "คู่มือทดสอบ\n## หัวข้อแรก\nเนื้อหาหัวข้อแรก"
    assert all(chunk.source == "guide.md" for chunk in chunks)


def test_split_long_text_respects_max_chars() -> None:
    text = "\n".join(f"บรรทัดที่ {i} " + "ก" * 30 for i in range(20))

    pieces = split_long_text(text, max_chars=100)

    assert len(pieces) > 1
    assert all(len(piece) <= 100 for piece in pieces)
    # ไม่มีข้อความหายระหว่างตัด
    assert "".join(pieces).replace("\n", "") == text.replace("\n", "")


def test_split_long_text_cuts_a_single_very_long_line() -> None:
    pieces = split_long_text("ข" * 250, max_chars=100)

    assert [len(piece) for piece in pieces] == [100, 100, 50]


def test_mock_kb_docs_are_chunked() -> None:
    chunks = load_chunks(DOCS_DIR)

    sources = {chunk.source for chunk in chunks}
    assert "pricing-plans.md" in sources
    assert len(sources) >= 5
    assert all(len(chunk.content) <= 800 for chunk in chunks)


# ---------- embedding ----------


def test_fake_embedder_gives_normalized_vectors_of_right_size() -> None:
    vector = FakeEmbedder().embed(["ราคา แพ็กเกจ"])[0]

    assert len(vector) == EMBEDDING_DIM
    assert sum(value * value for value in vector) == pytest.approx(1.0)


def make_ollama_embedder(handler: Any) -> OllamaEmbedder:
    client = httpx.Client(base_url="http://ollama.test", transport=httpx.MockTransport(handler))
    return OllamaEmbedder("http://ollama.test", "bge-m3", client=client)


def test_ollama_embedder_sends_texts_and_reads_vectors() -> None:
    sent: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        sent["path"] = request.url.path
        sent["body"] = json.loads(request.content)
        return httpx.Response(200, json={"embeddings": [[0.1] * EMBEDDING_DIM, [0.2] * EMBEDDING_DIM]})

    vectors = make_ollama_embedder(handler).embed(["a", "b"])

    assert sent == {"path": "/api/embed", "body": {"model": "bge-m3", "input": ["a", "b"]}}
    assert [vector[0] for vector in vectors] == [0.1, 0.2]


def test_ollama_embedder_rejects_wrong_dimension() -> None:
    embedder = make_ollama_embedder(lambda request: httpx.Response(200, json={"embeddings": [[0.1] * 3]}))

    with pytest.raises(LLMError, match="1024"):
        embedder.embed(["a"])


# ---------- ingest ----------


def write_docs(tmp_path: Path) -> Path:
    (tmp_path / "a.md").write_text(SAMPLE_DOC, encoding="utf-8")
    (tmp_path / "b.md").write_text("# อีกเอกสาร\n\nเนื้อหา", encoding="utf-8")
    (tmp_path / "ignore.txt").write_text("ไม่ใช่ markdown", encoding="utf-8")
    return tmp_path


def test_ingest_stores_chunks_with_embeddings(session: Session, tmp_path: Path) -> None:
    count = ingest_documents(session, FakeEmbedder(), write_docs(tmp_path))

    rows = session.exec(select(DocumentChunk).order_by(DocumentChunk.source, DocumentChunk.chunk_index)).all()
    assert count == 4
    assert [(row.source, row.chunk_index) for row in rows] == [
        ("a.md", 0),
        ("a.md", 1),
        ("a.md", 2),
        ("b.md", 0),
    ]
    assert len(rows[0].embedding) == EMBEDDING_DIM


def test_ingest_replaces_old_chunks(session: Session, tmp_path: Path) -> None:
    docs = write_docs(tmp_path)
    ingest_documents(session, FakeEmbedder(), docs)
    ingest_documents(session, FakeEmbedder(), docs)

    assert len(session.exec(select(DocumentChunk)).all()) == 4


def test_ingest_keeps_old_chunks_when_embedding_fails(session: Session, tmp_path: Path) -> None:
    docs = write_docs(tmp_path)
    ingest_documents(session, FakeEmbedder(), docs)

    class BrokenEmbedder(FakeEmbedder):
        def embed(self, texts: list[str]) -> list[list[float]]:
            raise LLMError("ต่อ Ollama ไม่ได้")

    with pytest.raises(LLMError):
        ingest_documents(session, BrokenEmbedder(), docs)

    assert len(session.exec(select(DocumentChunk)).all()) == 4


@pytest.mark.ollama
def test_ollama_real_embedding() -> None:
    from app.config import settings

    embedder = OllamaEmbedder(settings.ollama_base_url, settings.ollama_embed_model)

    vectors = embedder.embed(["ลืมรหัสผ่าน", "forgot password"])

    assert len(vectors) == 2
    assert all(len(vector) == EMBEDDING_DIM for vector in vectors)
