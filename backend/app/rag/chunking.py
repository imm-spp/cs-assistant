"""แบ่งเอกสาร markdown เป็นชิ้นเล็ก (chunk) ก่อนนำไปทำ embedding"""

from dataclasses import dataclass

MAX_CHARS = 800


@dataclass
class Chunk:
    source: str  # ชื่อไฟล์ต้นทาง เช่น pricing-plans.md
    index: int  # ลำดับของชิ้นในเอกสาร เริ่มที่ 0
    content: str


def split_sections(text: str) -> tuple[str, list[str]]:
    """แยกชื่อเอกสาร (# ...) และหัวข้อย่อย (## ...) ออกเป็นส่วน ๆ"""
    title = ""
    sections: list[list[str]] = [[]]

    for line in text.splitlines():
        if line.startswith("# ") and not title:
            title = line[2:].strip()
            continue
        if line.startswith("## "):
            sections.append([])
        sections[-1].append(line)

    texts = ["\n".join(lines).strip() for lines in sections]
    return title, [section for section in texts if section]


def split_long_text(text: str, max_chars: int) -> list[str]:
    """ถ้าข้อความยาวเกิน ให้ตัดตามบรรทัด รวมบรรทัดให้ได้ไม่เกิน max_chars ต่อชิ้น"""
    if len(text) <= max_chars:
        return [text]

    pieces: list[str] = []
    current = ""
    for line in text.splitlines():
        # บรรทัดเดียวที่ยาวเกินก็ต้องตัดตรง ๆ
        while len(line) > max_chars:
            pieces.append(line[:max_chars])
            line = line[max_chars:]
        if current and len(current) + 1 + len(line) > max_chars:
            pieces.append(current)
            current = line
        else:
            current = f"{current}\n{line}" if current else line
    if current.strip():
        pieces.append(current)
    return [piece.strip() for piece in pieces if piece.strip()]


def chunk_document(source: str, text: str, max_chars: int = MAX_CHARS) -> list[Chunk]:
    """แบ่งเอกสารหนึ่งไฟล์ แต่ละชิ้นขึ้นต้นด้วยชื่อเอกสาร เพื่อให้ค้นเจอง่ายและอ่านรู้เรื่อง"""
    title, sections = split_sections(text)
    prefix = f"{title}\n" if title else ""

    chunks: list[Chunk] = []
    for section in sections:
        for piece in split_long_text(section, max_chars - len(prefix)):
            chunks.append(Chunk(source=source, index=len(chunks), content=prefix + piece))
    return chunks
