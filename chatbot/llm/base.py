from __future__ import annotations

from typing import Protocol


class LLMClient(Protocol):

    @property
    def model(self) -> str: ...

    def chat(self, messages: list[dict]) -> str: ...
