from __future__ import annotations

from pathlib import Path

from chatbot.models import QuestionRun
from const import RUN_LOG_FILE


class RunLog:

    def __init__(self, path: Path = RUN_LOG_FILE):
        self._path = path

    def append(self, run: QuestionRun) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as f:
            f.write(run.model_dump_json() + "\n")
