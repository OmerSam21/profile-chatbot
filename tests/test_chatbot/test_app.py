from datetime import datetime
from unittest.mock import MagicMock

import pytest

from chatbot.answer_loop import Stage
from chatbot.app import _ERROR_MESSAGE, _EXHAUSTED_MESSAGE, ChatApp
from chatbot.models import Outcome, QuestionRun


def _record(outcome: Outcome, final_answer: str | None = None) -> QuestionRun:
    return QuestionRun(
        scenario_id="s",
        question="שאלה",
        started_at=datetime(2026, 11, 16),
        actor_model="a",
        critic_model="c",
        outcome=outcome,
        final_answer=final_answer,
    )


def _app(record: QuestionRun) -> ChatApp:
    loop = MagicMock()
    loop.run.return_value = iter([Stage.GENERATING, Stage.VALIDATING, record])
    return ChatApp(loop)


def _replies(app: ChatApp, request=None) -> list[str]:
    return list(app.respond("שאלה", [], request))


@pytest.mark.parametrize("record, expected", [
    (_record(Outcome.APPROVED, "תשובה מאושרת"), "תשובה מאושרת"),
    (_record(Outcome.ATTEMPTS_EXHAUSTED), _EXHAUSTED_MESSAGE),
    (_record(Outcome.TECHNICAL_ERROR), _ERROR_MESSAGE),
])
def test_final_reply_per_outcome(record, expected):
    assert _replies(_app(record))[-1] == expected


def test_live_status_before_final_reply():
    assert _replies(_app(_record(Outcome.APPROVED, "x")))[:2] == ["מנסח תשובה…", "מאמת את התשובה…"]


def test_session_hash_is_scenario_id():
    app = _app(_record(Outcome.APPROVED, "x"))
    _replies(app, MagicMock(session_hash="abc123"))
    assert app._loop.run.call_args.args[2] == "abc123"
