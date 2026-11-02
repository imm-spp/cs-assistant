"""นำเอกสารใน docs/mock-kb เข้าฐานข้อมูล: แบ่งชิ้น -> ทำ embedding -> บันทึก

รัน: cd backend && uv run python -m app.rag.ingest
"""

from pathlib import Path

from sqlmodel import Session, delete

from app.models import DocumentChunk
from app.rag.chunking import Chunk, chunk_document
from app.rag.embedding import Embedder

DOCS_DIR = Path(__file__).resolve().parents[3] / "docs" / "mock-kb"
BATCH_SIZE = 16


def load_chunks(docs_dir: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted(docs_dir.glob("*.md")):
        chunks.extend(chunk_document(path.name, path.read_text(encoding="utf-8")))
    return chunks


def ingest_documents(session: Session, embedder: Embedder, docs_dir: Path = DOCS_DIR) -> int:
    """ลบชิ้นเอกสารเดิมทั้งหมดแล้วนำเข้าใหม่ คืนค่าจำนวนชิ้นที่บันทึก"""
    chunks = load_chunks(docs_dir)

    # ทำ embedding ทีละกลุ่ม ก่อนแตะฐานข้อมูล ถ้า Ollama ล่มข้อมูลเดิมจะยังอยู่
    rows: list[DocumentChunk] = []
    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start : start + BATCH_SIZE]
        vectors = embedder.embed([chunk.content for chunk in batch])
        for chunk, vector in zip(batch, vectors, strict=True):
            rows.append(
                DocumentChunk(
                    source=chunk.source,
                    chunk_index=chunk.index,
                    content=chunk.content,
                    embedding=vector,
                )
            )

    session.exec(delete(DocumentChunk))
    session.add_all(rows)
    session.commit()
    return len(rows)


if __name__ == "__main__":
    from app.db import create_db_and_tables, engine
    from app.rag.embedding import get_embedder

    create_db_and_tables()
    with Session(engine) as session:
        count = ingest_documents(session, get_embedder())
    print(f"ingested {count} chunks from {DOCS_DIR}")
