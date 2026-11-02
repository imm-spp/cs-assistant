from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
from sqlmodel import Field, SQLModel

from app.rag.embedding import EMBEDDING_DIM


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Customer(SQLModel, table=True):
    """ลูกค้า (mock data เท่านั้น)"""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True)
    phone: str
    company: str
    tier: str = "standard"  # standard | premium | enterprise
    notes: str = ""
    created_at: datetime = Field(default_factory=utc_now)


class DocumentChunk(SQLModel, table=True):
    """ชิ้นเอกสารจาก docs/mock-kb พร้อม embedding สำหรับค้นหา (RAG)"""

    id: int | None = Field(default=None, primary_key=True)
    source: str = Field(index=True)  # ชื่อไฟล์ เช่น pricing-plans.md
    chunk_index: int
    content: str
    embedding: list[float] = Field(sa_column=Column(Vector(EMBEDDING_DIM), nullable=False))
