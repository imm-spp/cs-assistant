# CS Assistant — ผู้ช่วย AI สำหรับทีมดูแลลูกค้า

โปรเจคฝึกสหกิจ: เว็บหลังบ้านที่ช่วยทีม CS สรุปลูกค้า ร่างข้อความ TH/EN
และตอบคำถามจากเอกสาร (RAG) รันบน Ollama หรือ cloud API ได้

## กติกาที่ห้ามละเมิด
- ใช้ mock data เท่านั้น ห้ามใส่ข้อมูลลูกค้าจริง ชื่อ/อีเมล/เบอร์ต้องเป็นของปลอมจาก seed script
- ทุกฟีเจอร์ต้องมีเทสต์ และเทสต์ต้องผ่านก่อน commit
- ทำทีละฟีเจอร์ และ commit ทีละฟีเจอร์ (Conventional Commits เช่น `feat: customer list`)
- ห้าม commit ไฟล์ `.env` หรือ API key

## Stack
- backend/: Python 3.12, FastAPI, SQLModel, psycopg, pgvector, uv, pytest
- frontend/: React + Vite + TypeScript, Vitest + React Testing Library
- DB: PostgreSQL 16 + pgvector ผ่าน docker compose
- LLM: adapter ใน backend/app/llm/ (ollama | cloud | fake)

## โครงสร้าง
```
backend/app/
  main.py, config.py, db.py, models.py
  routers/     # customers, ai, rag
  services/    # business logic (summary, draft)
  llm/         # base.py (LLMProvider), ollama.py, cloud.py, fake.py, factory.py
  rag/         # chunking, embedding, retrieval
backend/tests/
backend/seed/  # สร้าง mock customers
docs/mock-kb/  # เอกสาร mock สำหรับ RAG
frontend/src/
```

## คำสั่ง
- เปิด DB:              `docker compose up -d`
- backend dev:          `cd backend && uv run fastapi dev app/main.py`
- backend test:         `cd backend && uv run pytest`
- เทสต์กับ Ollama จริง:  `cd backend && uv run pytest -m ollama`
- seed ข้อมูล:           `cd backend && uv run python -m seed`
- นำเอกสารเข้า RAG:      `cd backend && uv run python -m app.rag.ingest` (ต้องเปิด Ollama)
- frontend dev:         `cd frontend && npm run dev`
- frontend test:        `cd frontend && npm test`

## Config (.env, ดูตัวอย่างใน .env.example)
- `LLM_PROVIDER=ollama | cloud | fake`
- `OLLAMA_BASE_URL`, `OLLAMA_CHAT_MODEL=qwen2.5:7b`, `OLLAMA_EMBED_MODEL=bge-m3`
- `ANTHROPIC_API_KEY`, `CLOUD_CHAT_MODEL`
- `DATABASE_URL`, `TEST_DATABASE_URL`

## แนวทางเขียนโค้ด
- โค้ดใน router และ service ต้องเรียก LLM ผ่าน `get_llm()` เท่านั้น ห้าม import provider ตรง ๆ
- Embedding ใช้ Ollama เสมอ (มิติ vector ต้องคงที่)
- เทสต์ใช้ FakeProvider และ test DB แยก ห้ามเรียก LLM จริงในเทสต์ปกติ
- prompt เก็บเป็น constant ใน services/ เพื่อให้แก้และรีวิวได้ง่าย
- เขียนให้อ่านง่ายสำหรับมือใหม่ ใส่ type hints และไม่ใช้ abstraction เกินจำเป็น
