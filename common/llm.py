"""Pick the LLM backend from LLM_PROVIDER and build an OpenAI-compatible client for it.

Both backends speak the OpenAI chat-completions API, so only the endpoint, key,
model name, and thinking switch differ. Override per run without editing .env:
    LLM_PROVIDER=ollama python -m chapter01_summary.test
"""
import os

from dotenv import load_dotenv
from openai import OpenAI

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


def get_client_and_model():
    """Return (client, model) for the configured provider."""
    if get_provider() == "ollama":
        # Ollama ignores the key, but the OpenAI client refuses to start without one.
        client = OpenAI(api_key="ollama", base_url=_require("OLLAMA_BASE_URL"))
        return client, _require("OLLAMA_MODEL")
    client = OpenAI(api_key=_require("DASHSCOPE_API_KEY"), base_url=_require("DASHSCOPE_BASE_URL"))
    return client, _require("DASHSCOPE_MODEL")


def thinking_extra_body():
    """Request params that turn on the model's thinking phase for this provider."""
    if get_provider() == "ollama":
        return {"reasoning_effort": "medium"}
    return {"enable_thinking": True}


def reasoning_text(delta):
    """Reasoning text in a streamed delta: DashScope calls it reasoning_content, Ollama calls it reasoning."""
    return getattr(delta, "reasoning_content", None) or getattr(delta, "reasoning", None)
