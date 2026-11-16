from unittest.mock import MagicMock

import pytest
from openai import OpenAIError
from pydantic import BaseModel, ValidationError

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


class _Verdict(BaseModel):
    ok: bool


def _client_parsing(parsed: _Verdict | None) -> OpenAICompatibleClient:
    openai = MagicMock()
    openai.chat.completions.parse.return_value.choices[0].message.parsed = parsed
    return OpenAICompatibleClient(openai, "test-model")


def _validation_error() -> ValidationError:
    try:
        _Verdict.model_validate({})
    except ValidationError as e:
        return e


def test_parse_returns_parsed_model():
    assert _client_parsing(_Verdict(ok=True)).parse(_MESSAGES, _Verdict) == _Verdict(ok=True)


def test_parse_sends_response_format():
    client = _client_parsing(_Verdict(ok=True))
    client.parse(_MESSAGES, _Verdict)
    client._client.chat.completions.parse.assert_called_once_with(model="test-model", messages=_MESSAGES, response_format=_Verdict)


def test_parse_missing_parsed_raises():
    with pytest.raises(LLMError):
        _client_parsing(None).parse(_MESSAGES, _Verdict)


@pytest.mark.parametrize("error", [OpenAIError("boom"), _validation_error()])
def test_parse_api_or_validation_error_raises_llm_error(error):
    client = _client_parsing(_Verdict(ok=True))
    client._client.chat.completions.parse.side_effect = error
    with pytest.raises(LLMError):
        client.parse(_MESSAGES, _Verdict)
