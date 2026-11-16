from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime
from enum import StrEnum

from chatbot.actor import Actor
from chatbot.critic import Critic
from chatbot.exceptions import LLMError
from chatbot.models import Attempt, Outcome, QuestionRun
from chatbot.run_log import RunLog
from const import MAX_ATTEMPTS
from logging_utils import get_logger


class Stage(StrEnum):
    GENERATING = "generating"
    VALIDATING = "validating"


class AnswerLoop:

    def __init__(self, actor: Actor, critic: Critic, run_log: RunLog | None = None, max_attempts: int = MAX_ATTEMPTS):
        self._actor = actor
        self._critic = critic
        self._run_log = run_log or RunLog()
        self._max_attempts = max_attempts
        self._logger = get_logger(self.__class__.__name__)

    def run(self, question: str, history: list[dict], scenario_id: str) -> Iterator[Stage | QuestionRun]:
        record = QuestionRun(
            scenario_id=scenario_id,
            question=question,
            started_at=datetime.now(),
            actor_model=self._actor.model,
            critic_model=self._critic.model,
        )
        rejected_answer = feedback = None

        try:
            for number in range(1, self._max_attempts + 1):
                attempt = Attempt(number=number)
                record.attempts.append(attempt)

                yield Stage.GENERATING
                attempt.answer = self._actor.answer(question, history, rejected_answer, feedback)

                yield Stage.VALIDATING
                evaluation = self._critic.evaluate(question, attempt.answer, history)
                attempt.evaluation_completed = True
                attempt.is_acceptable = evaluation.is_acceptable
                attempt.feedback = evaluation.feedback

                if evaluation.is_acceptable:
                    record.outcome = Outcome.APPROVED
                    record.final_answer = attempt.answer
                    break
                rejected_answer, feedback = attempt.answer, evaluation.feedback
            else:
                record.outcome = Outcome.ATTEMPTS_EXHAUSTED
        except LLMError as e:
            attempt.error = str(e)
            record.outcome = Outcome.TECHNICAL_ERROR
            record.error = str(e)

        self._run_log.append(record)
        self._logger.info(
            "Question finished",
            extra={"extra_data": {
                "scenario_id": scenario_id,
                "outcome": record.outcome,
                "attempts": len(record.attempts),
            }},
        )
        yield record
