from __future__ import annotations

from pydantic import BaseModel, Field


class Evaluation(BaseModel):
    is_acceptable: bool = Field(description="True only if the answer meets all the criteria")
    feedback: str = Field(description="Short reason; on rejection, the exact problem and how to fix it")
