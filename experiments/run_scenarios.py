from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from chatbot.actor import Actor
from chatbot.answer_loop import AnswerLoop
from chatbot.app import build_actor_and_critic, final_message
from chatbot.critic import Critic
from chatbot.models import Attempt, Outcome, QuestionRun
from chatbot.run_log import RunLog
from const import RESULTS_DIR
from experiments.scenarios import SCENARIOS, AlwaysRejectCritic, PlantedFirstDraftActor, Scenario
from logging_utils import get_logger

logger = get_logger(__name__)

_RUNS_FILE = RESULTS_DIR / "scenarios.jsonl"
_SUMMARY_FILE = RESULTS_DIR / "summary.md"


@dataclass(frozen=True)
class ScenarioResult:
    scenario: Scenario
    runs: tuple[QuestionRun, ...]

    @property
    def matched(self) -> bool:
        return self.scenario.check(list(self.runs))


def run_scenario(scenario: Scenario, actor: Actor, critic: Critic, run_log: RunLog) -> ScenarioResult:
    if scenario.planted_draft:
        actor = PlantedFirstDraftActor(actor, scenario.planted_draft)
    if scenario.mock_critic:
        critic = AlwaysRejectCritic()
    loop = AnswerLoop(actor, critic, run_log)

    history: list[dict] = []
    runs = []
    for question in scenario.turns:
        run = list(loop.run(question, history, scenario.id))[-1]
        runs.append(run)
        history += [{"role": "user", "content": question}, {"role": "assistant", "content": final_message(run)}]
    return ScenarioResult(scenario, tuple(runs))


def _quote(text: str) -> str:
    return "\n".join(f"> {line}" if line else ">" for line in text.splitlines())


def _setup(scenario: Scenario) -> str:
    if scenario.mock_critic:
        return "mock Critic"
    if scenario.planted_draft:
        return "real models, planted first draft"
    return "real models"


def _verdict(attempt: Attempt) -> str:
    if not attempt.evaluation_completed:
        return "evaluation not completed"
    return "approved" if attempt.is_acceptable else "rejected"


def _render_run(run: QuestionRun) -> list[str]:
    lines = [f"Question: {run.question}", ""]
    for attempt in run.attempts:
        lines += [f"Attempt {attempt.number} ({_verdict(attempt)}):", "", _quote(attempt.answer or "(no answer)"), ""]
        if attempt.feedback:
            lines += [f"Critic: {attempt.feedback}", ""]
        if attempt.error:
            lines += [f"Error: {attempt.error}", ""]
    if run.outcome == Outcome.APPROVED:
        lines += [f"Shown to the user: the answer from attempt {len(run.attempts)}.", ""]
    else:
        lines += ["Shown to the user:", "", _quote(final_message(run)), ""]
    return lines


def _render_scenario(result: ScenarioResult) -> list[str]:
    scenario = result.scenario
    lines = [
        f"### {scenario.id}. {scenario.name}",
        "",
        f"Expected: {scenario.expectation}",
        "",
        f"Matched: {'yes' if result.matched else 'no'}",
        "",
    ]
    for run in result.runs:
        lines += _render_run(run)
    return lines


def render_summary(results: list[ScenarioResult], generated_at: datetime) -> str:
    first = results[0].runs[0]
    lines = [
        "# Scenario results",
        "",
        f"Run on {generated_at:%Y-%m-%d %H:%M} with `uv run python -m experiments.run_scenarios`.",
        f"Actor `{first.actor_model}`, Critic `{first.critic_model}`. Full records are in `scenarios.jsonl`.",
        "",
        "| # | Scenario | Setup | Outcome | Attempts | Matched |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        outcomes = ", ".join(run.outcome for run in r.runs)
        attempts = ", ".join(str(len(run.attempts)) for run in r.runs)
        lines.append(f"| {r.scenario.id} | {r.scenario.name} | {_setup(r.scenario)} | {outcomes} | {attempts} | {'yes' if r.matched else 'no'} |")

    lines += ["", "## LLM results", ""]
    for r in results:
        if not r.scenario.mock_critic:
            lines += _render_scenario(r)

    lines += ["## Mock control-flow test", "", "This Critic rejects every answer on purpose, to test the attempt limit.", ""]
    for r in results:
        if r.scenario.mock_critic:
            lines += _render_scenario(r)
    return "\n".join(lines)


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    _RUNS_FILE.unlink(missing_ok=True)
    actor, critic = build_actor_and_critic()
    run_log = RunLog(_RUNS_FILE)

    results = []
    for scenario in SCENARIOS:
        result = run_scenario(scenario, actor, critic, run_log)
        results.append(result)
        logger.info("Scenario finished", extra={"extra_data": {"scenario_id": scenario.id, "matched": result.matched}})

    _SUMMARY_FILE.write_text(render_summary(results, datetime.now()), encoding="utf-8")
    logger.info("Results written", extra={"extra_data": {"summary": str(_SUMMARY_FILE), "runs": str(_RUNS_FILE)}})


if __name__ == "__main__":
    main()
