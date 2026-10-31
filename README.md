# CS Assistant

ผู้ช่วย AI สำหรับทีมดูแลลูกค้า (โปรเจคฝึกสหกิจ) ใช้ mock data เท่านั้น

## สิ่งที่ต้องติดตั้ง
- Python 3.12 + [uv](https://docs.astral.sh/uv/)
- Node.js 20 ขึ้นไป
- Docker Desktop (สำหรับ PostgreSQL + pgvector)
- [Ollama](https://ollama.com/) (สำหรับรัน LLM ในเครื่อง)

## เริ่มต้น
```bash
cp .env.example .env
docker compose up -d

cd backend
uv sync
uv run fastapi dev app/main.py     # http://localhost:8000/docs

cd ../frontend
npm install
npm run dev                         # http://localhost:5173
```

## รันเทสต์
```bash
cd backend && uv run pytest
cd frontend && npm test
```

ดูรายละเอียดโครงสร้างและกติกาของโปรเจกต์ได้ใน [CLAUDE.md](CLAUDE.md)
