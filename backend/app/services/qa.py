"""ตอบคำถามจากเอกสาร (RAG): ค้นชิ้นเอกสาร -> ส่งให้ LLM ตอบโดยอ้างอิงเอกสารเท่านั้น"""

from sqlmodel import Session

from app.llm import LLMProvider
from app.rag.embedding import Embedder
from app.rag.retrieval import SearchResult, search_chunks

NO_DOCUMENTS_ANSWER = "ยังไม่มีเอกสารในระบบ ให้รัน python -m app.rag.ingest ก่อน"
NOT_FOUND_ANSWER = "ไม่พบข้อมูลในเอกสาร"

# ชิ้นเอกสารที่คะแนนต่ำกว่านี้ถือว่าไม่เกี่ยวกับคำถาม (วัดกับ bge-m3:
# คำถามที่เกี่ยวข้องได้ ~0.6-0.75 คำถามนอกเรื่องได้ ~0.35)
MIN_SCORE = 0.45

# prompt เก็บเป็น constant เพื่อให้แก้และรีวิวได้ง่าย
# การตัดสินว่า "ไม่พบข้อมูล" ทำในโค้ดด้วย MIN_SCORE ไม่ฝากให้โมเดลตัดสิน
# เพราะโมเดลเล็กมักตอบว่าไม่พบ ทั้งที่เอกสารมีคำตอบ
QA_SYSTEM_PROMPT = """\
คุณเป็นผู้ช่วยของทีมดูแลลูกค้า (Customer Support)
หน้าที่: ตอบคำถามของทีม โดยใช้ข้อมูลจาก "เอกสารอ้างอิง" ที่ให้มา
เอกสารเหล่านี้ถูกค้นมาแล้วว่าเกี่ยวข้องกับคำถาม คำตอบมักอยู่ในเอกสาร

กติกา:
- ตอบเป็นภาษาที่ระบุใน "ตอบเป็นภาษา"
- ตอบสั้น ตรงประเด็น ถ้ามีขั้นตอนให้เขียนเป็นข้อ ๆ
- ใส่ตัวเลข เวลา และเงื่อนไขให้ตรงตามเอกสาร
- ถ้าเอกสารตอบได้แค่บางส่วน ให้ตอบส่วนที่มี และบอกว่าส่วนไหนไม่มีในเอกสาร
- ห้ามแต่งข้อมูลที่ไม่มีในเอกสาร
- บรรทัดสุดท้ายเขียนแหล่งที่มา เช่น (ที่มา: pricing-plans.md)
"""


def contains_thai(text: str) -> bool:
    return any("฀" <= char <= "๿" for char in text)


def build_qa_prompt(question: str, results: list[SearchResult]) -> str:
    documents = "\n\n".join(
        f"[เอกสาร {i}: {result.source}]\n{result.content}" for i, result in enumerate(results, start=1)
    )
    language = "ภาษาไทย" if contains_thai(question) else "English"
    return (
        f"เอกสารอ้างอิง:\n\n{documents}\n\n"
        f"คำถาม: {question}\n"
        f"ตอบเป็นภาษา: {language}\n"
        "\nตอบคำถามโดยใช้ข้อมูลจากเอกสารด้านบน"
    )


def answer_question(
    session: Session, embedder: Embedder, llm: LLMProvider, question: str
) -> tuple[str, list[SearchResult]]:
    """คืนคำตอบ และชิ้นเอกสารที่ใช้ตอบ (ให้หน้าเว็บแสดงแหล่งที่มา)"""
    results = search_chunks(session, embedder, question)
    if not results:
        return NO_DOCUMENTS_ANSWER, []

    relevant = [result for result in results if result.score >= MIN_SCORE]
    if not relevant:
        return NOT_FOUND_ANSWER, []

    answer = llm.chat(QA_SYSTEM_PROMPT, build_qa_prompt(question, relevant)).strip()
    return answer, relevant
