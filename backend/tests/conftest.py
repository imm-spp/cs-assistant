from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app import models  # noqa: F401  (ให้ SQLModel รู้จักตาราง)
from app.config import settings
from app.db import get_session
from app.main import app

# ใช้ test DB แยก ไม่แตะข้อมูลใน dev DB
test_engine = create_engine(settings.test_database_url)


@pytest.fixture
def session() -> Iterator[Session]:
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def client(session: Session) -> Iterator[TestClient]:
    app.dependency_overrides[get_session] = lambda: session
    # ไม่ใช้ with TestClient(...) เพื่อไม่ให้ lifespan ไปสร้างตารางใน dev DB
    yield TestClient(app)
    app.dependency_overrides.clear()
