"""สร้างลูกค้าปลอมด้วย Faker — ห้ามใส่ข้อมูลลูกค้าจริง"""

import random

from faker import Faker
from sqlmodel import Session, delete

from app.models import Customer

TIERS = ["standard", "premium", "enterprise"]

# โน้ตตัวอย่างที่ทีม CS มักจดไว้ (แต่งขึ้นเองทั้งหมด) แยกตามภาษาของลูกค้า
THAI_NOTES = [
    "ขอใบเสนอราคาใหม่สำหรับการต่อสัญญาปีหน้า",
    "แจ้งปัญหาเข้าสู่ระบบไม่ได้ 2 ครั้งในสัปดาห์นี้ แก้ไขแล้ว",
    "สอบถามเรื่องเพิ่มจำนวนผู้ใช้จาก 10 เป็น 25 คน",
    "ไม่พอใจที่ทีมตอบอีเมลช้า ขอให้ติดต่อกลับภายในวันเดียวกัน",
    "ชำระเงินล่าช้า 15 วัน ฝ่ายบัญชีติดตามอยู่",
    "สนใจฟีเจอร์รายงานรายเดือน ขอเดโม",
    "ขอเปลี่ยนผู้ติดต่อหลักเป็นฝ่ายจัดซื้อ",
    "ชมทีมซัพพอร์ตว่าช่วยแก้ปัญหาได้เร็ว",
    "สัญญาจะหมดอายุสิ้นเดือนหน้า ยังไม่ได้ยืนยันการต่อ",
    "ขอใบกำกับภาษีย้อนหลัง 3 เดือน",
]

ENGLISH_NOTES = [
    "Requested a new quote for next year's renewal.",
    "Reported login issues twice this week; resolved.",
    "Asked about increasing seats from 10 to 25 users.",
    "Unhappy with slow email replies; wants same-day responses.",
    "Payment is 15 days overdue; finance is following up.",
    "Interested in the monthly reporting feature; asked for a demo.",
    "Wants to change the main contact to the procurement team.",
    "Praised the support team for fixing an issue quickly.",
    "Contract expires end of next month; renewal not confirmed yet.",
    "Requested invoices for the past 3 months.",
]


def build_fake_customers(count: int, seed: int = 42) -> list[Customer]:
    """สร้างลูกค้าปลอม count คน (ได้ผลเหมือนเดิมทุกครั้งถ้าใช้ seed เดิม)"""
    fake = Faker(["th_TH", "en_US"])
    fake.seed_instance(seed)
    rng = random.Random(seed)

    customers: list[Customer] = []
    for i in range(count):
        # สุ่มภาษาก่อน แล้วใช้ภาษาเดียวกันทั้งชื่อ บริษัท เบอร์ และโน้ต
        locale = rng.choice(["th_TH", "en_US"])
        notes = THAI_NOTES if locale == "th_TH" else ENGLISH_NOTES
        person = fake[locale]

        customers.append(
            Customer(
                name=person.name(),
                # ใช้โดเมน example.com เสมอ (จองไว้สำหรับตัวอย่าง ไม่มีใครใช้จริง)
                email=f"customer{i + 1}@example.com",
                phone=person.phone_number(),
                company=person.company(),
                tier=rng.choice(TIERS),
                notes=" ".join(rng.sample(notes, k=rng.randint(1, 3))),
            )
        )
    return customers


def seed_customers(session: Session, count: int = 30) -> int:
    """ลบลูกค้าเดิมทั้งหมดแล้วใส่ลูกค้าปลอมชุดใหม่ คืนค่าจำนวนที่ใส่"""
    session.exec(delete(Customer))
    session.add_all(build_fake_customers(count))
    session.commit()
    return count
