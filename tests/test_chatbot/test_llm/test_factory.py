from unittest.mock import patch

import pytest

from chatbot.llm.factory import create_llm_client

_FAKE_PROVIDERS = {
    "openai": ("sk-test", None),
    "gemini": ("", "https://gemini.example/"),
}


@patch("chatbot.llm.factory._PROVIDERS", _FAKE_PROVIDERS)
@patch("chatbot.llm.factory.OpenAI")
def test_factory_uses_provider_key_and_url(mock_openai):
    create_llm_client("openai", "gpt-test")
    mock_openai.assert_called_once_with(api_key="sk-test", base_url=None)


@patch("chatbot.llm.factory._PROVIDERS", _FAKE_PROVIDERS)
@patch("chatbot.llm.factory.OpenAI")
def test_factory_sets_model(mock_openai):
    assert create_llm_client("openai", "gpt-test").model == "gpt-test"


@patch("chatbot.llm.factory._PROVIDERS", _FAKE_PROVIDERS)
@pytest.mark.parametrize("provider", ["gemini", "unknown"])
def test_factory_rejects_missing_key_or_unknown_provider(provider):
    with pytest.raises(ValueError):
        create_llm_client(provider, "any-model")
