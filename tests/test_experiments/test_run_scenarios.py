from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from chatbot.models import Attempt, Outcome, QuestionRun
from experiments.run_scenarios import ScenarioResult, render_summary, run_scenario
from experiments.scenarios import SCENARIOS, AlwaysRejectCritic, PlantedFirstDraftActor

_BY_ID = {scenario.id: scenario for scenario in SCENARIOS}
_ANSWER = "תשובה (לפי פרופיל הלינקדאין)"


def _record(question: str = "q", outcome: Outcome = Outcome.APPROVED) -> QuestionRun:
    approved = outcome == Outcome.APPROVED
    return QuestionRun(
        scenario_id="x",
        question=question,
        started_at=datetime(2026, 11, 17),
        actor_model="actor-model",
        critic_model="critic-model",
        attempts=[Attempt(number=1, answer=_ANSWER, evaluation_completed=True, is_acceptable=approved, feedback="fb")],
        outcome=outcome,
        final_answer=_ANSWER if approved else None,
    )


@pytest.fixture
def loop_cls():
    with patch("experiments.run_scenarios.AnswerLoop") as cls:
        cls.return_value.run.side_effect = lambda question, history, scenario_id: iter([_record(question)])
        yield cls


def test_follow_up_history_holds_previous_shown_answer(loop_cls):
    run_scenario(_BY_ID["2"], MagicMock(), MagicMock(), MagicMock())
    second_history = loop_cls.return_value.run.call_args_list[1].args[1]
    assert second_history[1] == {"role": "assistant", "content": _ANSWER}


def test_runs_tagged_with_scenario_id(loop_cls):
    run_scenario(_BY_ID["1"], MagicMock(), MagicMock(), MagicMock())
    assert loop_cls.return_value.run.call_args.args[2] == "1"


def test_planted_scenario_wraps_actor(loop_cls):
    run_scenario(_BY_ID["4"], MagicMock(), MagicMock(), MagicMock())
    assert isinstance(loop_cls.call_args.args[0], PlantedFirstDraftActor)


def test_mock_scenario_swaps_critic(loop_cls):
    run_scenario(_BY_ID["5"], MagicMock(), MagicMock(), MagicMock())
    assert isinstance(loop_cls.call_args.args[1], AlwaysRejectCritic)


def _summary() -> str:
    results = [
        ScenarioResult(_BY_ID["1"], (_record("שאלה ראשונה"),)),
        ScenarioResult(_BY_ID["5"], (_record("איפה למדת?", Outcome.ATTEMPTS_EXHAUSTED),)),
    ]
    return render_summary(results, datetime(2026, 11, 17, 12, 0))


@pytest.mark.parametrize("text", ["## LLM results", "## Mock control-flow test", "שאלה ראשונה", "`attempts_exhausted`"])
def test_summary_contains(text):
    assert text in _summary()


def test_mock_scenario_rendered_after_mock_heading():
    summary = _summary()
    assert summary.index("### Scenario 5") > summary.index("## Mock control-flow test")
