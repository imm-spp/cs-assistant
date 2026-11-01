from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import Customer


def add_customers(session: Session) -> list[Customer]:
    customers = [
        Customer(name="Somchai Test", email="somchai@example.com", phone="000", company="Acme"),
        Customer(name="Alice Mock", email="alice@example.com", phone="111", company="Globex"),
    ]
    session.add_all(customers)
    session.commit()
    for customer in customers:
        session.refresh(customer)
    return customers


def test_list_customers_empty(client: TestClient) -> None:
    response = client.get("/api/customers")

    assert response.status_code == 200
    assert response.json() == []


def test_list_customers_sorted_by_name(client: TestClient, session: Session) -> None:
    add_customers(session)

    response = client.get("/api/customers")

    assert [c["name"] for c in response.json()] == ["Alice Mock", "Somchai Test"]


def test_search_customers_by_company(client: TestClient, session: Session) -> None:
    add_customers(session)

    response = client.get("/api/customers", params={"q": "glob"})

    assert [c["name"] for c in response.json()] == ["Alice Mock"]


def test_get_customer_by_id(client: TestClient, session: Session) -> None:
    somchai, _ = add_customers(session)

    response = client.get(f"/api/customers/{somchai.id}")

    assert response.status_code == 200
    assert response.json()["email"] == "somchai@example.com"


def test_get_missing_customer_returns_404(client: TestClient) -> None:
    response = client.get("/api/customers/9999")

    assert response.status_code == 404
