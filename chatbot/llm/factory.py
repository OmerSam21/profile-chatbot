from __future__ import annotations

from openai import OpenAI

from chatbot.llm.base import LLMClient
from chatbot.llm.openai_client import OpenAICompatibleClient
from const import GEMINI_BASE_URL, GOOGLE_API_KEY, OPENAI_API_KEY

# provider -> (api key, base url); None keeps the OpenAI default endpoint
_PROVIDERS = {
    "openai": (OPENAI_API_KEY, None),
    "gemini": (GOOGLE_API_KEY, GEMINI_BASE_URL),
}


def create_llm_client(provider: str, model: str) -> LLMClient:
    if provider not in _PROVIDERS:
        raise ValueError(f"Unknown LLM provider '{provider}', expected one of {sorted(_PROVIDERS)}")

    api_key, base_url = _PROVIDERS[provider]
    if not api_key:
        raise ValueError(f"{provider} provider requires an API key, set it in your .env file")

    return OpenAICompatibleClient(OpenAI(api_key=api_key, base_url=base_url), model)
