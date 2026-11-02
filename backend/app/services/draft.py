from typing import Literal

from app.llm import LLMProvider
from app.models import Customer

Language = Literal["th", "en"]

LANGUAGE_NAMES: dict[Language, str] = {"th": "ภาษาไทย", "en": "English"}

# prompt เก็บเป็น constant เพื่อให้แก้และรีวิวได้ง่าย
DRAFT_SYSTEM_PROMPT = """\
คุณเป็นผู้ช่วยของทีมดูแลลูกค้า (Customer Support)
หน้าที่: ร่างข้อความ (อีเมลหรือแชต) ถึงลูกค้า ตามที่ทีมสั่ง

กติกา:
- เขียนเป็นภาษาที่ระบุในคำสั่งเท่านั้น
- สุภาพ เป็นมืออาชีพ กระชับ ไม่เกิน 150 คำ
- ภาษาไทยให้ใช้ "เรียน คุณ<ชื่อ>" และลงท้ายด้วย "ทีมดูแลลูกค้า"
- ภาษาอังกฤษให้ใช้ "Dear <name>," และลงท้ายด้วย "Customer Support Team"
- ใช้เฉพาะข้อมูลที่ให้มา ห้ามแต่งตัวเลข วันที่ หรือข้อเสนอที่ไม่ได้บอก
- ตอบเฉพาะตัวข้อความที่จะส่ง ไม่ต้องอธิบายเพิ่ม
"""


def build_draft_prompt(customer: Customer, instruction: str, language: Language) -> str:
    """รวมข้อมูลลูกค้า + สิ่งที่ทีมอยากสื่อสาร เป็นข้อความสำหรับส่งให้ LLM"""
    return (
        "ข้อมูลลูกค้า:\n"
        f"- ชื่อ: {customer.name}\n"
        f"- บริษัท: {customer.company}\n"
        f"- ระดับ: {customer.tier}\n"
        f"- โน้ตจากทีม: {customer.notes or '(ไม่มี)'}\n"
        f"\nสิ่งที่ต้องการสื่อสาร: {instruction}\n"
        f"ภาษาที่ต้องใช้: {LANGUAGE_NAMES[language]}\n"
        "\nช่วยร่างข้อความถึงลูกค้ารายนี้"
    )


def draft_message(
    customer: Customer, instruction: str, language: Language, llm: LLMProvider
) -> str:
    prompt = build_draft_prompt(customer, instruction, language)
    return llm.chat(DRAFT_SYSTEM_PROMPT, prompt).strip()
