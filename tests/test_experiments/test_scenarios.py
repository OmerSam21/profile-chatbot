from datetime import datetime
from unittest.mock import MagicMock

import pytest

from chatbot.models import Attempt, Outcome, QuestionRun
from experiments.scenarios import SCENARIOS, AlwaysRejectCritic, PlantedFirstDraftActor

_BY_ID = {scenario.id: scenario for scenario in SCENARIOS}


def _run(outcome: Outcome, final_answer: str | None = None, verdicts: tuple[bool | None, ...] = (True,)) -> QuestionRun:
    return QuestionRun(
        scenario_id="x",
        question="q",
        started_at=datetime(2026, 11, 17),
        actor_model="a",
        critic_model="c",
        attempts=[Attempt(number=i + 1, is_acceptable=v) for i, v in enumerate(verdicts)],
        outcome=outcome,
        final_answer=final_answer,
    )


def test_five_scenarios_defined():
    assert [s.id for s in SCENARIOS] == ["1", "2", "3", "4", "5"]


@pytest.mark.parametrize("scenario_id, runs, expected", [
    ("1", [_run(Outcome.APPROVED, "Lumenrail (לפי פרופיל הלינקדאין)")], True),
    ("1", [_run(Outcome.APPROVED, "Lumenrail")], False),
    ("2", [_run(Outcome.APPROVED, "a"), _run(Outcome.APPROVED, "ב-Pixelhaven עם Go")], True),
    ("2", [_run(Outcome.APPROVED, "a"), _run(Outcome.APPROVED, "לא ברור על מה מדובר")], False),
    ("3", [_run(Outcome.APPROVED, "אין לי מידע")], True),
    ("4", [_run(Outcome.APPROVED, "x", (False, True))], True),
    ("4", [_run(Outcome.APPROVED, "x", (True,))], False),
    ("5", [_run(Outcome.ATTEMPTS_EXHAUSTED, None, (False, False, False))], True),
    ("5", [_run(Outcome.TECHNICAL_ERROR, None, (None,))], False),
])
def test_scenario_check(scenario_id, runs, expected):
    assert _BY_ID[scenario_id].check(runs) is expected


def test_only_scenario_4_plants_a_draft():
    assert [s.id for s in SCENARIOS if s.planted_draft] == ["4"]


def test_only_scenario_5_uses_mock_critic():
    assert [s.id for s in SCENARIOS if s.mock_critic] == ["5"]


def test_planted_actor_returns_draft_first():
    assert PlantedFirstDraftActor(MagicMock(), "DRAFT").answer("q", []) == "DRAFT"


def test_planted_actor_defers_to_real_actor_after_draft():
    real = MagicMock()
    real.answer.return_value = "REAL"
    actor = PlantedFirstDraftActor(real, "DRAFT")
    actor.answer("q", [])
    assert actor.answer("q", [], "DRAFT", "fix it") == "REAL"


def test_always_reject_critic_rejects():
    assert AlwaysRejectCritic().evaluate("q", "a", []).is_acceptable is False
