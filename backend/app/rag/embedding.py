"""แปลงข้อความเป็น vector (embedding) — ใช้ Ollama เสมอ เพื่อให้มิติ vector คงที่"""

import hashlib
import math
import re
from abc import ABC, abstractmethod

import httpx

from app.config import settings
from app.llm import LLMError

# bge-m3 ให้ vector 1024 มิติ ถ้าเปลี่ยนโมเดลต้องแก้ค่านี้และสร้างตารางใหม่
EMBEDDING_DIM = 1024


class Embedder(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """คืน vector หนึ่งตัวต่อข้อความหนึ่งข้อความ เรียงตามลำดับเดิม"""


class OllamaEmbedder(Embedder):
    def __init__(self, base_url: str, model: str, client: httpx.Client | None = None) -> None:
        self.model = model
        self.client = client or httpx.Client(base_url=base_url, timeout=120.0)

    def embed(self, texts: list[str]) -> list[list[float]]:
        try:
            response = self.client.post("/api/embed", json={"model": self.model, "input": texts})
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            raise LLMError(f"Ollama ตอบ error {error.response.status_code}: {error.response.text}") from error
        except httpx.HTTPError as error:
            raise LLMError(f"ต่อ Ollama ไม่ได้: {error}") from error

        vectors: list[list[float]] = response.json()["embeddings"]
        if any(len(vector) != EMBEDDING_DIM for vector in vectors):
            raise LLMError(f"embedding ต้องมี {EMBEDDING_DIM} มิติ (ตรวจ OLLAMA_EMBED_MODEL)")
        return vectors


class FakeEmbedder(Embedder):
    """ใช้ในเทสต์: ข้อความที่มีคำเหมือนกันจะได้ vector ใกล้กัน โดยไม่ต้องเรียก Ollama"""

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * EMBEDDING_DIM
        for word in re.findall(r"\w+", text.lower()):
            bucket = int(hashlib.md5(word.encode()).hexdigest(), 16) % EMBEDDING_DIM
            vector[bucket] += 1.0
        length = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / length for value in vector]


def get_embedder() -> Embedder:
    """ใช้เป็น FastAPI dependency ได้ (เทสต์ override เป็น FakeEmbedder)"""
    return OllamaEmbedder(settings.ollama_base_url, settings.ollama_embed_model)
