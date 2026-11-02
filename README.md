# CS Assistant — ผู้ช่วย AI สำหรับทีมดูแลลูกค้า

โปรเจคฝึกสหกิจ: เว็บหลังบ้านที่ช่วยทีม Customer Support ทำงานเร็วขึ้นด้วย AI
รันได้ทั้งบนเครื่องตัวเอง (Ollama) และผ่าน cloud API

> ใช้ **mock data เท่านั้น** ชื่อ อีเมล เบอร์โทร และเอกสารทั้งหมดเป็นของปลอม
> (ลูกค้าสร้างจาก seed script, เอกสารเป็นของบริษัทสมมติ "MockDesk")

## ทำอะไรได้บ้าง

| ฟีเจอร์ | รายละเอียด |
|---|---|
| รายชื่อลูกค้า | ตารางลูกค้าพร้อมค้นหาจากชื่อ อีเมล หรือบริษัท |
| สรุปลูกค้า | AI สรุปข้อมูลและโน้ตของลูกค้าเป็นหัวข้อสั้น ๆ พร้อมเตือนเมื่อเป็นลูกค้าระดับ premium / enterprise |
| ร่างข้อความ TH/EN | พิมพ์ว่าอยากสื่อสารเรื่องอะไร เลือกภาษา แล้ว AI ร่างอีเมลให้ แก้ไขต่อและคัดลอกได้ |
| ถามจากเอกสาร (RAG) | ถามคำถามเป็นภาษาไทยหรืออังกฤษ AI ตอบจากคู่มือของบริษัท พร้อมบอกแหล่งที่มาและคะแนนความตรง ถ้าไม่มีในเอกสารจะตอบว่า "ไม่พบข้อมูลในเอกสาร" แทนการเดา |

## สถาปัตยกรรม

```
 เบราว์เซอร์
     │
     ▼
 React + Vite (frontend/)  ── /api ──►  FastAPI (backend/)
                                          │
                     ┌────────────────────┼─────────────────────┐
                     ▼                    ▼                     ▼
          PostgreSQL + pgvector     LLM adapter            Embedding
          (ลูกค้า + ชิ้นเอกสาร)     ollama | cloud | fake    Ollama bge-m3
                                     (get_llm())            (1024 มิติ)
```

- **LLM adapter**: ทุกฟีเจอร์เรียก AI ผ่าน `get_llm()` ตัวเดียว เปลี่ยนจาก Ollama เป็น cloud ได้ด้วยการแก้ `LLM_PROVIDER` ใน `.env` โดยไม่ต้องแก้โค้ด
- **RAG**: ตัดเอกสาร Markdown ตามหัวข้อ → แปลงเป็น vector ด้วย `bge-m3` → เก็บใน pgvector → ตอนถาม ค้นชิ้นที่ใกล้ที่สุด 4 ชิ้นด้วย cosine distance แล้วส่งให้ LLM ตอบ

### แนวคิดสำคัญ: ให้โค้ดตัดสินใจแทนโมเดลเล็ก

ตอนทดสอบกับ `qwen2.5:3b` บนเครื่องจริง พบว่าโมเดลเล็กทำตามกฎแบบมีเงื่อนไขได้ไม่ดี
เช่น เตือน VIP ผิดคน หรือตอบ "ไม่พบข้อมูล" ทั้งที่เอกสารมีคำตอบ จึงย้ายการตัดสินใจเหล่านี้มาไว้ในโค้ด

| ปัญหาที่เจอ | วิธีแก้ |
|---|---|
| เตือนลูกค้า VIP ผิดคน | โค้ดเช็ก tier แล้วเติมบรรทัดเตือนเอง |
| bullet ซ้อน เช่น `- - ข้อความ` | โค้ดจัดรูปแบบ bullet ให้ใหม่ |
| คำขึ้นต้น/ลงท้ายปนสองภาษา | ส่งเฉพาะกฎของภาษาที่เลือก |
| ถามเรื่องที่ไม่เกี่ยวแล้ว AI แต่งคำตอบ | ตัดเอกสารที่คะแนนต่ำกว่า 0.45 ทิ้ง ถ้าไม่เหลือเลยตอบ "ไม่พบข้อมูล" โดยไม่เรียก AI |
| ถามเป็นภาษาอังกฤษแต่ตอบภาษาไทย | โค้ดตรวจภาษาของคำถามแล้วบอกโมเดลตรง ๆ |

ผลลัพธ์: คำถาม RAG ที่มีคำตอบในเอกสาร ตอบถูกจาก 1/4 เป็น 4/4 และสรุป/ร่างข้อความไม่มีข้อผิดพลาดข้างต้นอีก

## Tech stack

- **Backend**: Python 3.12, FastAPI, SQLModel, psycopg, pgvector, uv, pytest
- **Frontend**: React, Vite, TypeScript, Vitest, React Testing Library
- **Database**: PostgreSQL 16 + pgvector (Docker)
- **AI**: Ollama (`qwen2.5:3b` หรือ `qwen2.5:7b` สำหรับแชต, `bge-m3` สำหรับ embedding) หรือ Claude API

## สิ่งที่ต้องติดตั้ง

- Python 3.12 + [uv](https://docs.astral.sh/uv/)
- Node.js 20 ขึ้นไป
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Ollama](https://ollama.com/)

## ติดตั้งครั้งแรก

```bash
# 1. ตั้งค่า
cp .env.example .env

# 2. โหลดโมเดล AI (3b ใช้แรมประมาณ 2 GB, 7b ประมาณ 5 GB)
ollama pull qwen2.5:3b
ollama pull bge-m3

# 3. เปิดฐานข้อมูล
docker compose up -d

# 4. ติดตั้ง backend + ใส่ข้อมูลตัวอย่าง
cd backend
uv sync
uv run python -m seed              # สร้างลูกค้าปลอม 30 คน
uv run python -m app.rag.ingest    # นำเอกสารใน docs/mock-kb เข้า RAG (ต้องเปิด Ollama)

# 5. ติดตั้ง frontend
cd ../frontend
npm install
```

ถ้าใช้ `qwen2.5:3b` ให้แก้ `.env` เป็น `OLLAMA_CHAT_MODEL=qwen2.5:3b`

## เปิดใช้งาน

เปิด Docker Desktop และ Ollama ไว้ แล้วเปิด terminal 2 หน้าต่าง

```bash
# terminal 1 — backend
cd backend
uv run fastapi dev app/main.py     # API docs: http://localhost:8000/docs

# terminal 2 — frontend
cd frontend
npm run dev                        # เว็บ: http://localhost:5173
```

## ตั้งค่า (.env)

| ตัวแปร | ความหมาย |
|---|---|
| `LLM_PROVIDER` | `ollama` (ในเครื่อง), `cloud` (Claude API) หรือ `fake` (ไม่เรียก AI แค่สะท้อน prompt กลับมา ไว้ลองหน้าเว็บ — แต่ถามจากเอกสารยังต้องใช้ Ollama สำหรับ embedding) |
| `OLLAMA_CHAT_MODEL` | โมเดลแชต เช่น `qwen2.5:3b` (เร็ว ใช้แรมน้อย) หรือ `qwen2.5:7b` (ฉลาดกว่า) |
| `OLLAMA_EMBED_MODEL` | โมเดล embedding (`bge-m3`) |
| `ANTHROPIC_API_KEY`, `CLOUD_CHAT_MODEL` | ใช้เมื่อ `LLM_PROVIDER=cloud` |
| `DATABASE_URL`, `TEST_DATABASE_URL` | ฐานข้อมูลหลักและฐานข้อมูลสำหรับเทสต์ |

## API

| Method | Path | ใช้ทำอะไร |
|---|---|---|
| GET | `/api/customers?q=` | รายชื่อลูกค้า (ค้นหาได้) |
| GET | `/api/customers/{id}` | ข้อมูลลูกค้า 1 คน |
| POST | `/api/ai/customers/{id}/summary` | สรุปลูกค้า |
| POST | `/api/ai/customers/{id}/draft` | ร่างข้อความ `{instruction, language: "th" \| "en"}` |
| POST | `/api/rag/ask` | ถามจากเอกสาร `{question}` → `{answer, sources}` |

## เทสต์

```bash
cd backend && uv run pytest          # 61 เทสต์ ใช้ FakeProvider + test DB แยก ไม่เรียก AI จริง
cd backend && uv run pytest -m ollama  # เทสต์กับ Ollama จริง (ต้องเปิด Ollama)
cd frontend && npm test              # 18 เทสต์
```

## โครงสร้างโฟลเดอร์

```
backend/app/
  routers/     # customers, ai, rag (API endpoints)
  services/    # summary, draft, qa (prompt + logic)
  llm/         # LLMProvider, ollama, cloud, fake, get_llm()
  rag/         # chunking, embedding, ingest, retrieval
backend/seed/  # สร้างลูกค้า mock
backend/tests/
docs/mock-kb/  # เอกสาร mock ของ MockDesk สำหรับ RAG
frontend/src/  # หน้าเว็บ React
```

กติกาการพัฒนาและรายละเอียดเพิ่มเติมอยู่ใน [CLAUDE.md](CLAUDE.md)

## ข้อจำกัดที่รู้อยู่

- โมเดล `3b` บางครั้งเลือกคำไทยแปลก ๆ เวลาแปลโน้ตภาษาอังกฤษ และอาจตีความคำถามที่มีหลายเงื่อนไขผิดบางส่วน ถ้าแรมพอ แนะนำ `7b` หรือ cloud
- โหมด cloud เขียนไว้แล้วแต่ยังไม่ได้ทดสอบกับ API จริง
- ยังไม่มีระบบล็อกอิน ตั้งใจให้รันในเครื่องสำหรับเดโมเท่านั้น
