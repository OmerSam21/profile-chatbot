from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class Evaluation(BaseModel):
    is_acceptable: bool = Field(description="True only if the answer meets all the criteria")
    feedback: str = Field(description="Short reason; on rejection, the exact problem and how to fix it")


class Outcome(StrEnum):
    APPROVED = "approved"
    ATTEMPTS_EXHAUSTED = "attempts_exhausted"
    TECHNICAL_ERROR = "technical_error"


class Attempt(BaseModel):
    number: int
    answer: str | None = None
    evaluation_completed: bool = False
    is_acceptable: bool | None = None
    feedback: str | None = None
    error: str | None = None


class QuestionRun(BaseModel):
    scenario_id: str
    question: str
    started_at: datetime
    actor_model: str
    critic_model: str
    attempts: list[Attempt] = Field(default_factory=list)
    outcome: Outcome | None = None
    final_answer: str | None = None
    error: str | None = None
