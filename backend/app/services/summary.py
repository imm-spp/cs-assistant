from app.llm import LLMProvider
from app.models import Customer

# prompt เก็บเป็น constant เพื่อให้แก้และรีวิวได้ง่าย
SUMMARY_SYSTEM_PROMPT = """\
คุณเป็นผู้ช่วยของทีมดูแลลูกค้า (Customer Support)
หน้าที่: สรุปข้อมูลลูกค้าให้ทีมอ่านเข้าใจภายใน 10 วินาที

กติกา:
- ตอบเป็นภาษาไทย
- เขียน 3-5 bullet สั้น ๆ ขึ้นต้นด้วย "- "
- บอกว่าลูกค้าเป็นใคร อยู่บริษัทไหน ระดับ (tier) อะไร และประเด็นสำคัญจากโน้ต
- ถ้าเป็นลูกค้าระดับ premium หรือ enterprise ให้เตือนว่าควรดูแลเป็นพิเศษ
- ใช้เฉพาะข้อมูลที่ให้มา ห้ามแต่งข้อมูลเพิ่ม
"""


def build_customer_prompt(customer: Customer) -> str:
    """แปลงข้อมูลลูกค้าเป็นข้อความสำหรับส่งให้ LLM"""
    return (
        "ข้อมูลลูกค้า:\n"
        f"- ชื่อ: {customer.name}\n"
        f"- บริษัท: {customer.company}\n"
        f"- อีเมล: {customer.email}\n"
        f"- เบอร์โทร: {customer.phone}\n"
        f"- ระดับ: {customer.tier}\n"
        f"- โน้ตจากทีม: {customer.notes or '(ไม่มี)'}\n"
        "\nช่วยสรุปลูกค้ารายนี้"
    )


def summarize_customer(customer: Customer, llm: LLMProvider) -> str:
    return llm.chat(SUMMARY_SYSTEM_PROMPT, build_customer_prompt(customer)).strip()
