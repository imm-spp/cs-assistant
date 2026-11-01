import json
from types import SimpleNamespace
from typing import Any

import httpx
import pytest

from app.config import settings
from app.llm import LLMError, get_llm
from app.llm.cloud import CloudProvider
from app.llm.fake import FakeProvider
from app.llm.ollama import OllamaProvider

# ---------- factory ----------


@pytest.mark.parametrize(
    ("provider", "expected"),
    [("ollama", OllamaProvider), ("fake", FakeProvider)],
)
def test_get_llm_picks_provider(
    monkeypatch: pytest.MonkeyPatch, provider: str, expected: type
) -> None:
    monkeypatch.setattr(settings, "llm_provider", provider)

    assert isinstance(get_llm(), expected)


def test_get_llm_cloud_with_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "llm_provider", "cloud")
    monkeypatch.setattr(settings, "anthropic_api_key", "test-key")

    assert isinstance(get_llm(), CloudProvider)


def test_get_llm_cloud_without_key_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "llm_provider", "cloud")
    monkeypatch.setattr(settings, "anthropic_api_key", "")

    with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
        get_llm()


def test_get_llm_unknown_provider_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "llm_provider", "gpt")

    with pytest.raises(ValueError, match="gpt"):
        get_llm()


# ---------- fake ----------


def test_fake_provider_records_calls() -> None:
    llm = FakeProvider()

    assert llm.chat("be nice", "hello") == "[fake] hello"
    assert llm.calls == [("be nice", "hello")]


def test_fake_provider_fixed_reply() -> None:
    assert FakeProvider(reply="สวัสดี").chat("s", "u") == "สวัสดี"


# ---------- ollama (ใช้ MockTransport ไม่ต่อ Ollama จริง) ----------


def make_ollama(handler: Any) -> OllamaProvider:
    client = httpx.Client(base_url="http://ollama.test", transport=httpx.MockTransport(handler))
    return OllamaProvider("http://ollama.test", "qwen2.5:7b", client=client)


def test_ollama_sends_messages_and_reads_reply() -> None:
    sent: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        sent["path"] = request.url.path
        sent["body"] = json.loads(request.content)
        return httpx.Response(200, json={"message": {"role": "assistant", "content": "ok!"}})

    reply = make_ollama(handler).chat("system text", "user text")

    assert reply == "ok!"
    assert sent["path"] == "/api/chat"
    assert sent["body"] == {
        "model": "qwen2.5:7b",
        "messages": [
            {"role": "system", "content": "system text"},
            {"role": "user", "content": "user text"},
        ],
        "stream": False,
    }


def test_ollama_error_status_raises_llm_error() -> None:
    llm = make_ollama(lambda request: httpx.Response(404, text="model not found"))

    with pytest.raises(LLMError, match="404"):
        llm.chat("s", "u")


def test_ollama_connection_error_raises_llm_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    with pytest.raises(LLMError, match="ต่อ Ollama ไม่ได้"):
        make_ollama(handler).chat("s", "u")


# ---------- cloud (ใช้ client ปลอม ไม่เรียก API จริง) ----------


class StubMessages:
    def __init__(self, response: Any) -> None:
        self.response = response
        self.kwargs: dict[str, Any] = {}

    def create(self, **kwargs: Any) -> Any:
        self.kwargs = kwargs
        return self.response


def make_cloud(response: Any) -> tuple[CloudProvider, StubMessages]:
    messages = StubMessages(response)
    client = SimpleNamespace(beta=SimpleNamespace(messages=messages))
    return CloudProvider("test-key", "claude-sonnet-5-5", client=client), messages


def test_cloud_returns_text_blocks_only() -> None:
    response = SimpleNamespace(
        stop_reason="end_turn",
        content=[
            SimpleNamespace(type="thinking", thinking=""),
            SimpleNamespace(type="text", text="สวัสดีครับ"),
        ],
    )
    llm, messages = make_cloud(response)

    assert llm.chat("system text", "user text") == "สวัสดีครับ"
    assert messages.kwargs["model"] == "claude-sonnet-5-5"
    assert messages.kwargs["system"] == "system text"
    assert messages.kwargs["messages"] == [{"role": "user", "content": "user text"}]


def test_cloud_refusal_raises_llm_error() -> None:
    llm, _ = make_cloud(SimpleNamespace(stop_reason="refusal", content=[]))

    with pytest.raises(LLMError, match="ปฏิเสธ"):
        llm.chat("s", "u")


# ---------- เรียก Ollama จริง (รันเฉพาะ: uv run pytest -m ollama) ----------


@pytest.mark.ollama
def test_ollama_real_chat() -> None:
    llm = OllamaProvider(settings.ollama_base_url, settings.ollama_chat_model)

    reply = llm.chat("ตอบสั้น ๆ ไม่เกิน 5 คำ", "Say hello in Thai")

    assert reply.strip() != ""
