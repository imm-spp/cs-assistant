from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Customer(SQLModel, table=True):
    """ลูกค้า (mock data เท่านั้น)"""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True)
    phone: str
    company: str
    tier: str = "standard"  # standard | premium | enterprise
    notes: str = ""
    created_at: datetime = Field(default_factory=utc_now)
