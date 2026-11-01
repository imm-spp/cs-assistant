from app.config import settings
from app.llm.base import LLMProvider
from app.llm.cloud import CloudProvider
from app.llm.fake import FakeProvider
from app.llm.ollama import OllamaProvider


def get_llm() -> LLMProvider:
    """เลือก LLM ตาม LLM_PROVIDER ใน .env (ollama | cloud | fake)

    ใช้เป็น FastAPI dependency ได้: llm: LLMProvider = Depends(get_llm)
    """
    provider = settings.llm_provider

    if provider == "ollama":
        return OllamaProvider(settings.ollama_base_url, settings.ollama_chat_model)
    if provider == "cloud":
        if not settings.anthropic_api_key:
            raise ValueError("LLM_PROVIDER=cloud ต้องตั้งค่า ANTHROPIC_API_KEY ใน .env")
        return CloudProvider(settings.anthropic_api_key, settings.cloud_chat_model)
    if provider == "fake":
        return FakeProvider()

    raise ValueError(f"ไม่รู้จัก LLM_PROVIDER={provider!r} (ใช้ได้: ollama, cloud, fake)")
