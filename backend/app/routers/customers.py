from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, col, or_, select

from app.db import get_session
from app.models import Customer

router = APIRouter(prefix="/api/customers", tags=["customers"])


@router.get("")
def list_customers(
    q: str | None = None,
    session: Session = Depends(get_session),
) -> list[Customer]:
    """รายชื่อลูกค้าทั้งหมด ค้นหาด้วย q ได้ (ชื่อ อีเมล หรือบริษัท)"""
    query = select(Customer).order_by(col(Customer.name))
    if q:
        pattern = f"%{q}%"
        query = query.where(
            or_(
                col(Customer.name).ilike(pattern),
                col(Customer.email).ilike(pattern),
                col(Customer.company).ilike(pattern),
            )
        )
    return list(session.exec(query).all())


@router.get("/{customer_id}")
def get_customer(customer_id: int, session: Session = Depends(get_session)) -> Customer:
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
