from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# ไฟล์ .env อยู่ที่ root ของโปรเจกต์ (เหนือ backend/ หนึ่งชั้น)
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    database_url: str = "postgresql+psycopg://cs:cs@localhost:5432/cs_assistant"
    test_database_url: str = "postgresql+psycopg://cs:cs@localhost:5432/cs_assistant_test"


settings = Settings()
