from __future__ import annotations

from openai import OpenAI, OpenAIError

from chatbot.exceptions import LLMError
from logging_utils import get_logger

logger = get_logger(__name__)


class OpenAICompatibleClient:

    def __init__(self, client: OpenAI, model: str):
        self._client = client
        self._model = model

    @property
    def model(self) -> str:
        return self._model

    def chat(self, messages: list[dict]) -> str:
        try:
            response = self._client.chat.completions.create(model=self._model, messages=messages)
        except OpenAIError as e:
            raise LLMError(f"{self._model} call failed: {e}") from e

        content = response.choices[0].message.content
        if not content:
            raise LLMError(f"{self._model} returned an empty response")

        logger.info(
            "LLM chat complete",
            extra={"extra_data": {"model": self._model, "messages": len(messages), "response_length": len(content)}},
        )
        return content
