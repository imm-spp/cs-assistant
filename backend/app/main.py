from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import create_db_and_tables
from app.routers import ai, customers, rag


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    create_db_and_tables()
    yield


app = FastAPI(title="CS Assistant API", lifespan=lifespan)
app.include_router(customers.router)
app.include_router(ai.router)
app.include_router(rag.router)


@app.get("/api/health")
def health() -> dict[str, str]:
    """ใช้เช็กว่า backend รันอยู่"""
    return {"status": "ok"}
