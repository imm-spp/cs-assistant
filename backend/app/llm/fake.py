from app.llm.base import LLMProvider


class FakeProvider(LLMProvider):
    """ใช้ในเทสต์: ไม่เรียกโมเดลจริง ตอบเหมือนเดิมทุกครั้ง และจำว่าถูกเรียกด้วยอะไร"""

    name = "fake"

    def __init__(self, reply: str | None = None) -> None:
        # ถ้าไม่กำหนด reply จะตอบโดยสะท้อนข้อความผู้ใช้กลับไป
        self.reply = reply
        self.calls: list[tuple[str, str]] = []

    def chat(self, system: str, user: str) -> str:
        self.calls.append((system, user))
        if self.reply is not None:
            return self.reply
        return f"[fake] {user}"
