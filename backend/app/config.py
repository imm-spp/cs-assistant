from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# ไฟล์ .env อยู่ที่ root ของโปรเจกต์ (เหนือ backend/ หนึ่งชั้น)
ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    database_url: str = "postgresql+psycopg://cs:cs@localhost:5432/cs_assistant"
    test_database_url: str = "postgresql+psycopg://cs:cs@localhost:5432/cs_assistant_test"

    # LLM: ollama | cloud | fake
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "qwen2.5:7b"
    ollama_embed_model: str = "bge-m3"
    anthropic_api_key: str = ""
    cloud_chat_model: str = "claude-sonnet-5-5"


settings = Settings()
