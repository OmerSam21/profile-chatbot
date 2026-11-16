from unittest.mock import MagicMock

import pytest

from chatbot.actor import Actor

_HISTORY = [
    {"role": "user", "content": "Where do you work?"},
    {"role": "assistant", "content": "Lumenrail"},
]


def _actor() -> Actor:
    llm = MagicMock()
    llm.chat.return_value = "Answer"
    return Actor(llm, "SYSTEM")


def _sent_messages(actor: Actor) -> list[dict]:
    return actor._llm.chat.call_args.args[0]


def test_answer_returns_llm_reply():
    assert _actor().answer("Hi", []) == "Answer"


def test_answer_sends_system_history_then_question():
    actor = _actor()
    actor.answer("And before that?", _HISTORY)
    assert _sent_messages(actor) == [{"role": "system", "content": "SYSTEM"}, *_HISTORY, {"role": "user", "content": "And before that?"}]


def test_answer_does_not_mutate_history():
    history = list(_HISTORY)
    _actor().answer("And before that?", history)
    assert history == _HISTORY


def _sent_system_prompt(actor: Actor) -> str:
    return _sent_messages(actor)[0]["content"]


def test_first_attempt_keeps_plain_system_prompt():
    actor = _actor()
    actor.answer("Where?", [])
    assert _sent_system_prompt(actor) == "SYSTEM"


@pytest.mark.parametrize("text", ["I worked at Google", "Remove the Google claim"])
def test_revision_adds_rejected_answer_and_feedback(text):
    actor = _actor()
    actor.answer("Where?", [], rejected_answer="I worked at Google", feedback="Remove the Google claim")
    assert text in _sent_system_prompt(actor)
