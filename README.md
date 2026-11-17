# Profile Chatbot

A Hebrew chatbot that answers visitors' questions about one person, based on their LinkedIn profile and a short personal summary.
Every answer is written by an **Actor** model and checked by a separate **Critic** model before it is shown.
A rejected answer goes back to the Actor with the Critic's feedback, up to 3 attempts per question.

The profile in `profile/` is a fictional sample person.

See [docs/architecture.md](docs/architecture.md) for the flow diagram and the three exit paths, and [docs/report.pdf](docs/report.pdf) for the short report (Hebrew, built from `docs/report.html`).

## Requirements

- Python 3.12
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Free API keys for [Google AI Studio](https://aistudio.google.com/apikey) (Actor) and [Groq](https://console.groq.com/keys) (Critic)

## Setup

### With uv

```bash
uv sync
```

uv creates `.venv` with Python 3.12 and installs the locked dependencies.

### With pip

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
```

### Environment

Copy `.env.example` to `.env` and fill in the keys:

```
GOOGLE_API_KEY=...
GROQ_API_KEY=...
```

`.env` is gitignored. The app checks at startup that every provider in use has a key.

## Running the chat

```bash
uv run python -m chatbot.app
```

With pip, activate `.venv` and run `python -m chatbot.app`. The chat opens at http://127.0.0.1:7860.

Each question is logged to `logs/runs.jsonl` with every attempt, the Critic's decision and feedback, and the outcome (`approved`, `attempts_exhausted` or `technical_error`).

## Running the tests

```bash
uv run pytest
```

The unit tests mock all model calls and need no API keys.

## Running the scenarios

```bash
uv run python -m experiments.run_scenarios
```

Runs the five assignment scenarios against the real models and writes `results/summary.md` and `results/scenarios.jsonl`. Scenario 4 plants a flawed first draft, and scenario 5 uses a mock Critic that rejects everything to test the attempt limit.
The committed results and a manual review of them are in [results/](results/).

## Models and settings

| Setting | Value used in the experiments |
|---|---|
| Actor | `gemini-3.1-flash-lite` (Gemini API, OpenAI-compatible endpoint) |
| Critic | `openai/gpt-oss-120b` (Groq) |
| Max attempts per question | 3 |
| Sampling | Provider defaults |

Both roles are configurable in `.env` (`ACTOR_PROVIDER`, `ACTOR_MODEL`, `CRITIC_PROVIDER`, `CRITIC_MODEL`). Supported providers are `gemini`, `groq` and `openai`.

## Project layout

```
chatbot/
  app.py            Gradio chat UI and startup
  answer_loop.py    Actor -> Critic -> revise loop with the attempt limit
  actor.py          Answer generation
  critic.py         Answer evaluation
  context.py        Profile loading and all prompts
  models.py         Evaluation and run log models
  run_log.py        JSON Lines run log
  llm/              OpenAI-compatible client and provider factory
experiments/        Scenario definitions and runner
profile/            Sample LinkedIn profile and personal summary
results/            Scenario results and manual review
docs/               Architecture diagram and report
tests/              Unit tests
```
