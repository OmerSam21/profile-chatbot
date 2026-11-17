# Architecture

```mermaid
flowchart TD
    LI["profile/linkedin.txt"] --> CTX["context.py<br/>Actor and Critic prompts"]
    SU["profile/summary.txt"] --> CTX

    V(["Visitor"]) -->|"question"| UI["Gradio chat UI"]
    H[("Chat history<br/>questions + approved answers")] <--> UI
    UI -->|"question + history"| LOOP{{"AnswerLoop<br/>attempt n of 3"}}

    CTX -->|"Actor system prompt"| A
    CTX -->|"Critic system prompt"| C

    LOOP --> A["Actor<br/>default: gemini-3.1-flash-lite"]
    A -->|"candidate answer"| C["Critic<br/>default: openai/gpt-oss-120b on Groq"]
    C -->|"structured output"| E[/"Evaluation<br/>is_acceptable: bool<br/>feedback: str"/]

    E -->|"is_acceptable = true"| OK(["Exit: approved<br/>answer shown and added to history"])
    E -->|"false, attempts left"| FB["Rejected answer + feedback"]
    FB -->|"feedback arc: revise"| A
    E -->|"false on attempt 3"| EX(["Exit: attempts exhausted<br/>limit message shown"])

    A -.->|"model call failed"| ERR(["Exit: technical error<br/>error message shown"])
    C -.->|"call failed or invalid output"| ERR

    LOOP --> LOG[("logs/runs.jsonl<br/>one record per question")]

    classDef exit fill:#e8f5e9,stroke:#2e7d32
    classDef fail fill:#ffebee,stroke:#c62828
    class OK exit
    class EX,ERR fail
```

| Exit | When | Shown to the visitor | Run log `outcome` |
|---|---|---|---|
| Approved | The Critic accepts an answer | The answer | `approved` |
| Attempts exhausted | All 3 answers are rejected | A message that no accurate answer was found within 3 attempts | `attempts_exhausted` |
| Technical error | A model call fails, or the Critic output does not match `Evaluation` | A technical error message | `technical_error` |

Each record in `logs/runs.jsonl` holds the scenario ID, the question and the outcome. Each attempt in it holds its number, the candidate answer, the Critic's decision and the feedback, or `evaluation_completed: false` when the evaluation did not finish.
