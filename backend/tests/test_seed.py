from sqlmodel import Session, select

from app.models import Customer
from seed import ENGLISH_NOTES, THAI_NOTES, build_fake_customers, seed_customers


def test_fake_customers_use_example_emails() -> None:
    customers = build_fake_customers(20)

    assert len(customers) == 20
    assert all(c.email.endswith("@example.com") for c in customers)
    assert len({c.email for c in customers}) == 20


def test_fake_customers_are_reproducible() -> None:
    first = [c.name for c in build_fake_customers(5)]
    second = [c.name for c in build_fake_customers(5)]

    assert first == second


def contains_thai(text: str) -> bool:
    return any("฀" <= char <= "๿" for char in text)


def test_notes_come_from_templates_in_matching_language() -> None:
    customers = build_fake_customers(30)

    for customer in customers:
        templates = THAI_NOTES if contains_thai(customer.name) else ENGLISH_NOTES
        assert customer.notes != ""
        # โน้ตต้องประกอบจากประโยคตัวอย่างภาษาเดียวกับชื่อลูกค้าเท่านั้น
        remaining = customer.notes
        for sentence in templates:
            remaining = remaining.replace(sentence, "")
        assert remaining.strip() == ""

    # ต้องมีลูกค้าทั้งไทยและอังกฤษ
    assert any(contains_thai(c.name) for c in customers)
    assert any(not contains_thai(c.name) for c in customers)


def test_seed_replaces_existing_customers(session: Session) -> None:
    seed_customers(session, count=10)
    seed_customers(session, count=10)

    assert len(session.exec(select(Customer)).all()) == 10
