"""ค้นหาชิ้นเอกสารที่ใกล้เคียงกับคำถามมากที่สุดด้วย pgvector"""

from dataclasses import dataclass

from sqlmodel import Session, col, select

from app.models import DocumentChunk
from app.rag.embedding import Embedder

TOP_K = 4


@dataclass
class SearchResult:
    source: str
    content: str
    score: float  # ความใกล้เคียง 0-1 (ยิ่งมากยิ่งตรง) = 1 - cosine distance


def search_chunks(
    session: Session, embedder: Embedder, question: str, top_k: int = TOP_K
) -> list[SearchResult]:
    question_vector = embedder.embed([question])[0]
    distance = col(DocumentChunk.embedding).cosine_distance(question_vector)

    rows = session.exec(
        select(DocumentChunk, distance.label("distance")).order_by(distance).limit(top_k)
    ).all()

    return [
        SearchResult(source=chunk.source, content=chunk.content, score=round(1 - dist, 4))
        for chunk, dist in rows
    ]
