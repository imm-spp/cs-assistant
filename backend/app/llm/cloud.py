from typing import Any

import anthropic

from app.llm.base import LLMError, LLMProvider


class CloudProvider(LLMProvider):
    """เรียก Claude ผ่าน Anthropic API (ต้องมี ANTHROPIC_API_KEY)"""

    name = "cloud"

    def __init__(self, api_key: str, model: str, client: Any | None = None) -> None:
        self.model = model
        # เทสต์ส่ง client ปลอมเข้ามาได้ จะได้ไม่เรียก API จริง
        self.client = client or anthropic.Anthropic(api_key=api_key)

    def chat(self, system: str, user: str) -> str:
        try:
            response = self.client.beta.messages.create(
                model=self.model,
                max_tokens=16000,
                system=system,
                messages=[{"role": "user", "content": user}],
                # ถ้าโมเดลปฏิเสธคำขอ (safety) ให้ API ลองโมเดลสำรองให้อัตโนมัติ
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
            )
        except anthropic.APIConnectionError as error:
            raise LLMError(f"ต่อ Anthropic API ไม่ได้: {error}") from error
        except anthropic.APIStatusError as error:
            raise LLMError(f"Anthropic API ตอบ error {error.status_code}: {error.message}") from error

        if response.stop_reason == "refusal":
            raise LLMError("โมเดลปฏิเสธคำขอนี้")

        # คำตอบมีได้หลาย block (เช่น thinking) เอาเฉพาะส่วนที่เป็นข้อความ
        return "".join(block.text for block in response.content if block.type == "text")
