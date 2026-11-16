from unittest.mock import MagicMock

import pytest
from openai import OpenAIError

from chatbot.exceptions import LLMError
from chatbot.llm.openai_client import OpenAICompatibleClient

_MESSAGES = [{"role": "user", "content": "Hi"}]


def _client_returning(content: str | None) -> OpenAICompatibleClient:
    openai = MagicMock()
    openai.chat.completions.create.return_value.choices[0].message.content = content
    return OpenAICompatibleClient(openai, "test-model")


def test_chat_returns_message_content():
    assert _client_returning("Hello").chat(_MESSAGES) == "Hello"


def test_chat_sends_model_and_messages():
    client = _client_returning("Hello")
    client.chat(_MESSAGES)
    client._client.chat.completions.create.assert_called_once_with(model="test-model", messages=_MESSAGES)


@pytest.mark.parametrize("content", [None, ""])
def test_chat_empty_response_raises(content):
    with pytest.raises(LLMError):
        _client_returning(content).chat(_MESSAGES)


def test_chat_api_error_raises_llm_error():
    client = _client_returning("Hello")
    client._client.chat.completions.create.side_effect = OpenAIError("boom")
    with pytest.raises(LLMError):
        client.chat(_MESSAGES)
