"""ตอบคำถามจากเอกสาร (RAG): ค้นชิ้นเอกสาร -> ส่งให้ LLM ตอบโดยอ้างอิงเอกสารเท่านั้น"""

from sqlmodel import Session

from app.llm import LLMProvider
from app.rag.embedding import Embedder
from app.rag.retrieval import SearchResult, search_chunks

NO_DOCUMENTS_ANSWER = "ยังไม่มีเอกสารในระบบ ให้รัน python -m app.rag.ingest ก่อน"

# prompt เก็บเป็น constant เพื่อให้แก้และรีวิวได้ง่าย
QA_SYSTEM_PROMPT = """\
คุณเป็นผู้ช่วยของทีมดูแลลูกค้า (Customer Support)
หน้าที่: ตอบคำถามของทีม โดยใช้ข้อมูลจาก "เอกสารอ้างอิง" ที่ให้มาเท่านั้น

กติกา:
- ตอบเป็นภาษาเดียวกับคำถาม
- ตอบสั้น ตรงประเด็น ถ้ามีขั้นตอนให้เขียนเป็นข้อ ๆ
- ใส่ตัวเลข เวลา และเงื่อนไขให้ตรงตามเอกสาร
- ท้ายคำตอบให้บอกแหล่งที่มา เช่น (ที่มา: pricing-plans.md)
- ถ้าเอกสารไม่มีคำตอบ ให้ตอบว่า "ไม่พบข้อมูลในเอกสาร" ห้ามเดาหรือแต่งเพิ่ม
"""


def build_qa_prompt(question: str, results: list[SearchResult]) -> str:
    documents = "\n\n".join(
        f"[เอกสาร {i}: {result.source}]\n{result.content}" for i, result in enumerate(results, start=1)
    )
    return f"เอกสารอ้างอิง:\n\n{documents}\n\nคำถาม: {question}"


def answer_question(
    session: Session, embedder: Embedder, llm: LLMProvider, question: str
) -> tuple[str, list[SearchResult]]:
    """คืนคำตอบ และชิ้นเอกสารที่ใช้ตอบ (ให้หน้าเว็บแสดงแหล่งที่มา)"""
    results = search_chunks(session, embedder, question)
    if not results:
        return NO_DOCUMENTS_ANSWER, []

    answer = llm.chat(QA_SYSTEM_PROMPT, build_qa_prompt(question, results)).strip()
    return answer, results
