from unittest.mock import MagicMock, call

import pytest

from chatbot.answer_loop import AnswerLoop, Stage
from chatbot.exceptions import LLMError
from chatbot.models import Evaluation, Outcome, QuestionRun

_OK = Evaluation(is_acceptable=True, feedback="Grounded.")
_BAD = Evaluation(is_acceptable=False, feedback="Remove the Google claim.")


def _loop(answers: list, verdicts: list) -> AnswerLoop:
    actor, critic = MagicMock(model="actor-model"), MagicMock(model="critic-model")
    actor.answer.side_effect = answers
    critic.evaluate.side_effect = verdicts
    return AnswerLoop(actor, critic, run_log=MagicMock(), max_attempts=3)


def _run(loop: AnswerLoop) -> list:
    return list(loop.run("Where?", [], "1"))


def _record(loop: AnswerLoop) -> QuestionRun:
    return _run(loop)[-1]


@pytest.mark.parametrize("answers, verdicts, expected", [
    (["a1"], [_OK], Outcome.APPROVED),
    (["a1", "a2"], [_BAD, _OK], Outcome.APPROVED),
    (["a1", "a2", "a3"], [_BAD, _BAD, _BAD], Outcome.ATTEMPTS_EXHAUSTED),
    ([LLMError("down")], [], Outcome.TECHNICAL_ERROR),
    (["a1"], [LLMError("invalid output")], Outcome.TECHNICAL_ERROR),
])
def test_outcome(answers, verdicts, expected):
    assert _record(_loop(answers, verdicts)).outcome == expected


def test_approved_on_retry_returns_revised_answer():
    assert _record(_loop(["a1", "a2"], [_BAD, _OK])).final_answer == "a2"


def test_exhausted_has_no_final_answer():
    assert _record(_loop(["a1", "a2", "a3"], [_BAD, _BAD, _BAD])).final_answer is None


def test_exhausted_stops_after_max_attempts():
    loop = _loop(["a1", "a2", "a3", "a4"], [_BAD, _BAD, _BAD, _OK])
    _run(loop)
    assert loop._actor.answer.call_count == 3


def test_retry_passes_rejected_answer_and_feedback_to_actor():
    loop = _loop(["a1", "a2"], [_BAD, _OK])
    _run(loop)
    assert loop._actor.answer.call_args_list[1] == call("Where?", [], "a1", "Remove the Google claim.")


def test_first_attempt_has_no_revision_context():
    loop = _loop(["a1"], [_OK])
    _run(loop)
    assert loop._actor.answer.call_args_list[0] == call("Where?", [], None, None)


def test_critic_error_marks_evaluation_not_completed():
    assert _record(_loop(["a1"], [LLMError("invalid output")])).attempts[0].evaluation_completed is False


def test_critic_error_records_no_decision():
    assert _record(_loop(["a1"], [LLMError("invalid output")])).attempts[0].is_acceptable is None


def test_rejected_attempts_are_kept_in_record():
    record = _record(_loop(["a1", "a2", "a3"], [_BAD, _BAD, _BAD]))
    assert [a.answer for a in record.attempts] == ["a1", "a2", "a3"]


@pytest.mark.parametrize("verdicts", [[_OK], [LLMError("invalid output")]])
def test_every_question_is_logged_once(verdicts):
    loop = _loop(["a1"], verdicts)
    _run(loop)
    loop._run_log.append.assert_called_once()


def test_stages_before_record():
    assert _run(_loop(["a1"], [_OK]))[:2] == [Stage.GENERATING, Stage.VALIDATING]


def test_counter_resets_between_questions():
    loop = _loop(["a1", "a2", "b1"], [_BAD, _OK, _OK])
    _run(loop)
    assert len(_record(loop).attempts) == 1
