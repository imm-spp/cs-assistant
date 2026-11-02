import re

from app.llm import LLMProvider
from app.models import Customer

# ระดับลูกค้าที่ต้องดูแลเป็นพิเศษ
VIP_TIERS = {"premium", "enterprise"}

# prompt เก็บเป็น constant เพื่อให้แก้และรีวิวได้ง่าย
# คำเตือนลูกค้า VIP ไม่ให้โมเดลเขียน แต่โค้ดเติมเอง (โมเดลเล็กมักเตือนผิดคน)
SUMMARY_SYSTEM_PROMPT = """\
คุณเป็นผู้ช่วยของทีมดูแลลูกค้า (Customer Support)
หน้าที่: สรุปข้อมูลลูกค้าให้ทีมอ่านเข้าใจภายใน 10 วินาที

กติกา:
- ตอบเป็นภาษาไทยเท่านั้น
- เขียน 2-4 bullet สั้น ๆ แต่ละบรรทัดขึ้นต้นด้วย "- "
- bullet แรก: ชื่อลูกค้า บริษัท และระดับ
- bullet ถัดไป: ประเด็นจากโน้ต หนึ่งเรื่องต่อหนึ่ง bullet
- คัดลอกตัวเลขและช่วงเวลาจากโน้ตให้ตรงทุกตัว เช่น "เดือนหน้า" ห้ามเปลี่ยนเป็น "เดือนนี้"
- ไม่ต้องเขียนคำเตือนหรือคำแนะนำ
- ใช้เฉพาะข้อมูลที่ให้มา ห้ามแต่งข้อมูลเพิ่ม
"""


def build_customer_prompt(customer: Customer) -> str:
    """แปลงข้อมูลลูกค้าเป็นข้อความสำหรับส่งให้ LLM"""
    return (
        "ข้อมูลลูกค้า:\n"
        f"- ชื่อ: {customer.name}\n"
        f"- บริษัท: {customer.company}\n"
        f"- ระดับ: {customer.tier}\n"
        f"- โน้ตจากทีม: {customer.notes or '(ไม่มี)'}\n"
        "\nช่วยสรุปลูกค้ารายนี้"
    )


def clean_bullets(text: str) -> str:
    """แก้ bullet ซ้อนที่โมเดลเล็กชอบเขียน เช่น "- -ข้อความ" -> "- ข้อความ\""""
    lines = [re.sub(r"^\s*(?:[-*•]\s*)+", "- ", line) for line in text.strip().splitlines()]
    return "\n".join(line for line in lines if line.strip() not in {"", "-"})


def vip_warning(customer: Customer) -> str | None:
    if customer.tier in VIP_TIERS:
        return f"- ⚠️ ลูกค้าระดับ {customer.tier} ควรดูแลเป็นพิเศษ"
    return None


def summarize_customer(customer: Customer, llm: LLMProvider) -> str:
    summary = clean_bullets(llm.chat(SUMMARY_SYSTEM_PROMPT, build_customer_prompt(customer)))
    warning = vip_warning(customer)
    return f"{summary}\n{warning}" if warning else summary
