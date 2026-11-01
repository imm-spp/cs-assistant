from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

from app.config import settings

engine = create_engine(settings.database_url)


def create_db_and_tables() -> None:
    # import models เพื่อให้ SQLModel รู้จักตารางทั้งหมดก่อนสร้าง
    from app import models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    """FastAPI dependency: เปิด session ต่อหนึ่ง request"""
    with Session(engine) as session:
        yield session
