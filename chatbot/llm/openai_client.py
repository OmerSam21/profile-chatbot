from __future__ import annotations

from openai import OpenAI, OpenAIError
from pydantic import ValidationError

from chatbot.exceptions import LLMError
from chatbot.llm.base import T
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

    def parse(self, messages: list[dict], response_model: type[T]) -> T:
        try:
            response = self._client.chat.completions.parse(
                model=self._model,
                messages=messages,
                response_format=response_model,
            )
        except (OpenAIError, ValidationError) as e:
            raise LLMError(f"{self._model} structured call failed: {e}") from e

        parsed = response.choices[0].message.parsed
        if parsed is None:
            raise LLMError(f"{self._model} returned no valid {response_model.__name__}")

        logger.info(
            "LLM structured output parsed",
            extra={"extra_data": {"model": self._model, "response_model": response_model.__name__}},
        )
        return parsed
