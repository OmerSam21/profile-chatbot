from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from chatbot.actor import Actor
from chatbot.models import Evaluation, Outcome, QuestionRun

_PLANTED_DRAFT = "לפני Lumenrail עבדתי שלוש שנים כראש צוות ב-Google, שם הובלתי 20 מפתחים (לפי פרופיל הלינקדאין)."
_MOCK_FEEDBACK = "Mock critic: rejected on purpose to test the attempt limit."


class PlantedFirstDraftActor:

    def __init__(self, actor: Actor, draft: str):
        self._actor = actor
        self._draft = draft
        self._used = False

    @property
    def model(self) -> str:
        return f"{self._actor.model} (first draft planted)"

    def answer(self, question: str, history: list[dict], rejected_answer: str | None = None, feedback: str | None = None) -> str:
        if not self._used:
            self._used = True
            return self._draft
        return self._actor.answer(question, history, rejected_answer, feedback)


class AlwaysRejectCritic:
    model = "mock-always-reject (control-flow test)"

    def evaluate(self, question: str, answer: str, history: list[dict]) -> Evaluation:
        return Evaluation(is_acceptable=False, feedback=_MOCK_FEEDBACK)


@dataclass(frozen=True)
class Scenario:
    id: str
    name: str
    turns: tuple[str, ...]
    expectation: str
    check: Callable[[list[QuestionRun]], bool]
    planted_draft: str | None = None
    mock_critic: bool = False


def _approved(run: QuestionRun) -> bool:
    return run.outcome == Outcome.APPROVED


def _cites_source(runs: list[QuestionRun]) -> bool:
    return _approved(runs[0]) and "(לפי" in runs[0].final_answer


def _keeps_context(runs: list[QuestionRun]) -> bool:
    keywords = ("שנה ושבעה", "Go", "Kafka", "Pixelhaven")
    return all(_approved(run) for run in runs) and any(word in runs[1].final_answer for word in keywords)


def _rejected_then_revised(runs: list[QuestionRun]) -> bool:
    run = runs[0]
    return run.attempts[0].is_acceptable is False and len(run.attempts) >= 2 and _approved(run)


def _exhausted_after_three(runs: list[QuestionRun]) -> bool:
    run = runs[0]
    return run.outcome == Outcome.ATTEMPTS_EXHAUSTED and len(run.attempts) == 3


SCENARIOS = (
    Scenario(
        id="1",
        name="Existing information",
        turns=("באיזה תפקיד אתה עובד היום ומה הישג מרכזי שלך שם?",),
        expectation="An approved answer that points to the supporting detail in the sources.",
        check=_cites_source,
    ),
    Scenario(
        id="2",
        name="Follow-up question",
        turns=("איפה עבדת לפני Lumenrail?", "כמה זמן עבדת שם ובאילו טכנולוגיות השתמשת?"),
        expectation="Both turns approved, and the second resolves 'there' to the previous answer (Pixelhaven).",
        check=_keeps_context,
    ),
    Scenario(
        id="3",
        name="Detail not in the sources",
        turns=("באיזה תיכון למדת ומה היה ממוצע הבגרות שלך?",),
        expectation="An approved answer that says the information is not available, without inventing a personal fact.",
        check=lambda runs: _approved(runs[0]),
    ),
    Scenario(
        id="4",
        name="Rejection and revision",
        turns=("איפה עבדת לפני Lumenrail?",),
        expectation="The planted draft with an invented fact is rejected with a reason, then a revised answer is evaluated again and approved.",
        check=_rejected_then_revised,
        planted_draft=_PLANTED_DRAFT,
    ),
    Scenario(
        id="5",
        name="Attempts exhausted",
        turns=("איפה למדת?",),
        expectation="Three rejected attempts, a stop after the third, and the attempt-limit message.",
        check=_exhausted_after_three,
        mock_critic=True,
    ),
)
