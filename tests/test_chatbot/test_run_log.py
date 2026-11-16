from datetime import datetime

from chatbot.models import Attempt, Outcome, QuestionRun
from chatbot.run_log import RunLog


def _run(question: str) -> QuestionRun:
    return QuestionRun(
        scenario_id="1",
        question=question,
        started_at=datetime(2026, 11, 16, 12, 0),
        actor_model="actor",
        critic_model="critic",
        attempts=[Attempt(number=1, answer="תשובה", evaluation_completed=True, is_acceptable=True, feedback="ok")],
        outcome=Outcome.APPROVED,
        final_answer="תשובה",
    )


def _lines(tmp_path) -> list[str]:
    return (tmp_path / "logs" / "runs.jsonl").read_text(encoding="utf-8").splitlines()


def test_append_writes_one_line_per_run(tmp_path):
    log = RunLog(tmp_path / "logs" / "runs.jsonl")
    log.append(_run("first"))
    log.append(_run("second"))
    assert len(_lines(tmp_path)) == 2


def test_append_round_trips_run(tmp_path):
    RunLog(tmp_path / "logs" / "runs.jsonl").append(_run("שאלה"))
    assert QuestionRun.model_validate_json(_lines(tmp_path)[0]) == _run("שאלה")


def test_append_keeps_hebrew_readable(tmp_path):
    RunLog(tmp_path / "logs" / "runs.jsonl").append(_run("שאלה"))
    assert "שאלה" in _lines(tmp_path)[0]
