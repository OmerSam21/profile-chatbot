from unittest.mock import MagicMock

import gradio as gr
import pytest

from chatbot.app import ChatApp
from chatbot.exceptions import LLMError


def _app(reply: str | Exception) -> ChatApp:
    actor = MagicMock()
    actor.answer.side_effect = reply if isinstance(reply, Exception) else None
    actor.answer.return_value = reply
    return ChatApp(actor)


def test_respond_returns_actor_answer():
    assert _app("תשובה").respond("שאלה", []) == "תשובה"


def test_respond_passes_history_to_actor():
    app = _app("תשובה")
    history = [{"role": "user", "content": "היי"}]
    app.respond("שאלה", history)
    app._actor.answer.assert_called_once_with("שאלה", history)


def test_respond_llm_error_raises_gradio_error():
    with pytest.raises(gr.Error):
        _app(LLMError("down")).respond("שאלה", [])
