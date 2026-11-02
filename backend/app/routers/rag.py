from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.db import get_session
from app.llm import LLMError, LLMProvider, get_llm
from app.rag.embedding import Embedder, get_embedder
from app.services.qa import answer_question

router = APIRouter(prefix="/api/rag", tags=["rag"])


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


class Source(BaseModel):
    source: str
    content: str
    score: float


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]


@router.post("/ask")
def ask(
    request: AskRequest,
    session: Session = Depends(get_session),
    embedder: Embedder = Depends(get_embedder),
    llm: LLMProvider = Depends(get_llm),
) -> AskResponse:
    """ถามคำถามจากเอกสารใน docs/mock-kb"""
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=422, detail="question must not be blank")

    try:
        answer, results = answer_question(session, embedder, llm, question)
    except LLMError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error

    return AskResponse(
        answer=answer,
        sources=[Source(source=r.source, content=r.content, score=r.score) for r in results],
    )
