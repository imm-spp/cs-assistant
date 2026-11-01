from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from app.db import get_session
from app.llm import LLMError, LLMProvider, get_llm
from app.models import Customer
from app.services.summary import summarize_customer

router = APIRouter(prefix="/api/ai", tags=["ai"])


class SummaryResponse(BaseModel):
    customer_id: int
    summary: str


@router.post("/customers/{customer_id}/summary")
def customer_summary(
    customer_id: int,
    session: Session = Depends(get_session),
    llm: LLMProvider = Depends(get_llm),
) -> SummaryResponse:
    """ให้ AI สรุปข้อมูลลูกค้าหนึ่งราย"""
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    try:
        summary = summarize_customer(customer, llm)
    except LLMError as error:
        # 502 = backend ทำงานได้ แต่ระบบ AI ที่อยู่ข้างหลังมีปัญหา
        raise HTTPException(status_code=502, detail=str(error)) from error

    return SummaryResponse(customer_id=customer_id, summary=summary)
