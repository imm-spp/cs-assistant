from abc import ABC, abstractmethod


class LLMError(Exception):
    """เรียก LLM ไม่สำเร็จ (ต่อไม่ติด, ตอบ error, หรือโมเดลปฏิเสธคำขอ)"""


class LLMProvider(ABC):
    """หน้าตากลางของ LLM ทุกเจ้า router/service เรียกผ่าน get_llm() เท่านั้น"""

    name: str

    @abstractmethod
    def chat(self, system: str, user: str) -> str:
        """ส่ง system prompt + ข้อความผู้ใช้ แล้วคืนคำตอบเป็นข้อความ"""
