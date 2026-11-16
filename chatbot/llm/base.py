from __future__ import annotations

from typing import Protocol, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMClient(Protocol):

    @property
    def model(self) -> str: ...

    def chat(self, messages: list[dict]) -> str: ...

    def parse(self, messages: list[dict], response_model: type[T]) -> T: ...
