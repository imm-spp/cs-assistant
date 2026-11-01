from sqlmodel import Session, select

from app.models import Customer
from seed import build_fake_customers, seed_customers


def test_fake_customers_use_example_emails() -> None:
    customers = build_fake_customers(20)

    assert len(customers) == 20
    assert all(c.email.endswith("@example.com") for c in customers)
    assert len({c.email for c in customers}) == 20


def test_fake_customers_are_reproducible() -> None:
    first = [c.name for c in build_fake_customers(5)]
    second = [c.name for c in build_fake_customers(5)]

    assert first == second


def test_seed_replaces_existing_customers(session: Session) -> None:
    seed_customers(session, count=10)
    seed_customers(session, count=10)

    assert len(session.exec(select(Customer)).all()) == 10
