"""Pick the LLM backend from LLM_PROVIDER and build a LangChain chat model for it.

DashScope goes through ChatDeepSeek: it talks to any OpenAI-compatible endpoint and,
unlike ChatOpenAI, keeps the streamed reasoning_content. Ollama goes through ChatOllama,
which uses Ollama's native API. Override per run without editing .env:
    LLM_PROVIDER=ollama python -m chapter02_models.test
"""
import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()  # loads .env from the repo root; real OS env vars take precedence

PROVIDERS = ("dashscope", "ollama")


def _require(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} is not set; add it to .env (see .env.example)")
    return value


def get_provider():
    """Return the provider name."""
    provider = os.getenv("LLM_PROVIDER", "dashscope").strip().lower()
    if provider not in PROVIDERS:
        raise ValueError(f"LLM_PROVIDER={provider!r}; expected one of {PROVIDERS}")
    return provider


def get_chat_model(thinking=True):
    """Return a chat model for the configured provider, with the thinking phase on or off."""
    if get_provider() == "ollama":
        return init_chat_model(
            _require("OLLAMA_MODEL"),
            model_provider="ollama",
            base_url=_require("OLLAMA_BASE_URL"),
            reasoning=thinking,
        )
    return init_chat_model(
        _require("DASHSCOPE_MODEL"),
        model_provider="deepseek",
        api_key=_require("DASHSCOPE_API_KEY"),
        api_base=_require("DASHSCOPE_BASE_URL"),
        extra_body={"enable_thinking": thinking},
    )


def reasoning_text(chunk):
    """Reasoning text in a streamed AIMessageChunk; both providers put it in additional_kwargs."""
    return chunk.additional_kwargs.get("reasoning_content")
