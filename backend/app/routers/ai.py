from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.db import get_session
from app.llm import LLMError, LLMProvider, get_llm
from app.models import Customer
from app.services.draft import Language, draft_message
from app.services.summary import summarize_customer

router = APIRouter(prefix="/api/ai", tags=["ai"])


class SummaryResponse(BaseModel):
    customer_id: int
    summary: str


class DraftRequest(BaseModel):
    instruction: str = Field(min_length=1, max_length=1000)
    language: Language = "th"


class DraftResponse(BaseModel):
    customer_id: int
    language: Language
    draft: str


def get_customer_or_404(session: Session, customer_id: int) -> Customer:
    customer = session.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.post("/customers/{customer_id}/summary")
def customer_summary(
    customer_id: int,
    session: Session = Depends(get_session),
    llm: LLMProvider = Depends(get_llm),
) -> SummaryResponse:
    """ให้ AI สรุปข้อมูลลูกค้าหนึ่งราย"""
    customer = get_customer_or_404(session, customer_id)

    try:
        summary = summarize_customer(customer, llm)
    except LLMError as error:
        # 502 = backend ทำงานได้ แต่ระบบ AI ที่อยู่ข้างหลังมีปัญหา
        raise HTTPException(status_code=502, detail=str(error)) from error

    return SummaryResponse(customer_id=customer_id, summary=summary)


@router.post("/customers/{customer_id}/draft")
def customer_draft(
    customer_id: int,
    request: DraftRequest,
    session: Session = Depends(get_session),
    llm: LLMProvider = Depends(get_llm),
) -> DraftResponse:
    """ให้ AI ร่างข้อความถึงลูกค้า เป็นภาษาไทยหรืออังกฤษ"""
    customer = get_customer_or_404(session, customer_id)
    instruction = request.instruction.strip()
    if not instruction:
        raise HTTPException(status_code=422, detail="instruction must not be blank")

    try:
        draft = draft_message(customer, instruction, request.language, llm)
    except LLMError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    return DraftResponse(customer_id=customer_id, language=request.language, draft=draft)
