# Manual review of the scenario run

Reviewed run: `summary.md` generated on 2026-11-17 10:56.
Actor `gemini-3.1-flash-lite` (Gemini API), Critic `openai/gpt-oss-120b` (Groq), `MAX_ATTEMPTS=3`, provider default sampling settings.

## Did each scenario behave as expected?

| # | Scenario | Expected | Actual | Matched |
|---|---|---|---|---|
| 1 | Existing information | Approved answer citing the supporting detail | Approved on attempt 1, cites the LinkedIn profile for the role and the 780ms to 210ms latency cut | Yes |
| 2 | Follow-up question | Second turn uses the first answer | "שם" was read as Pixelhaven: 1 year 7 months, Go, Python, Kafka, Redis | Yes |
| 3 | Detail not in the sources | Says the information is missing, invents nothing | States that high school and matriculation grades are not in the sources, offers the B.Sc. GPA instead | Yes |
| 4 | Rejection and revision | Planted invented fact is rejected, revision is approved | Google claim rejected with criterion 1 and a concrete fix, attempt 2 lists the real prior roles and is approved | Yes |
| 5 | Attempts exhausted (mock Critic) | Three rejections, stop, limit message | Three rejected attempts, then the attempt-limit message; no rejected answer shown | Yes |

Scenario 5 uses a mock Critic and only tests control flow. Scenarios 1 to 4 use the real models.

## Approved answers checked against the sources

### Scenario 1

| Claim in the answer | Source | Supported |
|---|---|---|
| Senior Backend Engineer at Lumenrail | linkedin.txt, Experience | Yes |
| Lumenrail is a logistics SaaS for last-mile delivery | linkedin.txt, Experience | Yes |
| Led the move of route planning to an event-driven design, p95 780ms to 210ms | linkedin.txt, Experience | Yes |
| Built an LLM ticket triage service | linkedin.txt and summary.txt | Yes |
| Triage cut first-response time by 35%, cited as "(לפי הסיכום האישי)" | The 35% appears only in linkedin.txt | Fact yes, citation wrong |
| "I am very proud of" the triage service | summary.txt lists it next to the event-driven migration as a proudest project | Yes |

### Scenario 2, turn 2

| Claim in the answer | Source | Supported |
|---|---|---|
| Worked at Pixelhaven for 1 year 7 months | linkedin.txt, Experience | Yes |
| Used Go and Python | linkedin.txt: Go pipelines, Python reporting API | Yes |
| Kafka pipelines and Redis caching | linkedin.txt, Experience | Yes |
| C# and SQL Server during military service | linkedin.txt, Experience | Yes |

## Evaluator limitation found

In scenario 1 the Critic approved an answer that attributes the 35% figure to the personal summary, although it appears only in the LinkedIn profile. The Critic checks whether a fact exists somewhere in the sources, not whether the cited source is the right one. A valid `Evaluation` object only shows that the output matched the schema; the decision inside it can still be wrong.

## Notes

- LLM output varies between runs. This review covers the committed run only; rerunning the script overwrites `summary.md` and `scenarios.jsonl`.
- In an earlier exploratory run the Critic rejected the Actor's required "I am an AI" disclosure as an unsupported personal fact. The Critic prompt was corrected to treat statements about the chatbot itself as needing no source.
