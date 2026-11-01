import httpx

from app.llm.base import LLMError, LLMProvider


class OllamaProvider(LLMProvider):
    """เรียกโมเดลที่รันในเครื่องผ่าน Ollama HTTP API (POST /api/chat)"""

    name = "ollama"

    def __init__(self, base_url: str, model: str, client: httpx.Client | None = None) -> None:
        self.model = model
        # เทสต์ส่ง client ปลอมเข้ามาได้ (httpx.MockTransport)
        self.client = client or httpx.Client(base_url=base_url, timeout=120.0)

    def chat(self, system: str, user: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
        }
        try:
            response = self.client.post("/api/chat", json=payload)
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            raise LLMError(f"Ollama ตอบ error {error.response.status_code}: {error.response.text}") from error
        except httpx.HTTPError as error:
            raise LLMError(f"ต่อ Ollama ไม่ได้: {error}") from error

        return response.json()["message"]["content"]
