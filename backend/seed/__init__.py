"""สร้างลูกค้าปลอมด้วย Faker — ห้ามใส่ข้อมูลลูกค้าจริง"""

import random

from faker import Faker
from sqlmodel import Session, delete

from app.models import Customer

TIERS = ["standard", "premium", "enterprise"]


def build_fake_customers(count: int, seed: int = 42) -> list[Customer]:
    """สร้างลูกค้าปลอม count คน (ได้ผลเหมือนเดิมทุกครั้งถ้าใช้ seed เดิม)"""
    fake = Faker(["th_TH", "en_US"])
    fake.seed_instance(seed)
    rng = random.Random(seed)

    customers: list[Customer] = []
    for i in range(count):
        customers.append(
            Customer(
                name=fake.name(),
                # ใช้โดเมน example.com เสมอ (จองไว้สำหรับตัวอย่าง ไม่มีใครใช้จริง)
                email=f"customer{i + 1}@example.com",
                phone=fake.phone_number(),
                company=fake.company(),
                tier=rng.choice(TIERS),
                notes=fake.sentence(),
            )
        )
    return customers


def seed_customers(session: Session, count: int = 30) -> int:
    """ลบลูกค้าเดิมทั้งหมดแล้วใส่ลูกค้าปลอมชุดใหม่ คืนค่าจำนวนที่ใส่"""
    session.exec(delete(Customer))
    session.add_all(build_fake_customers(count))
    session.commit()
    return count
