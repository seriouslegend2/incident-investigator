# Assignment coverage

This is a status document, not a claim that every requirement is finished. “Runnable” means the checked-in demo does it today; “next” means it is designed but not yet demonstrated.

| Assignment requirement | Status | Evidence / next action |
| --- | --- | --- |
| Investigate a vague incident report using evidence | Runnable | D1 accepts a complaint and assigns bounded tasks. D3–D6 fetch scoped evidence; no diagnosis is stored in a scenario. |
| Multi-agent collaboration, not a linear set of prompts | Runnable | LangGraph shares durable case/task/evidence state. D1 fans out selected specialists in parallel, waits at a join, then D7 can send a precise follow-up through D1. |
| Orchestrator, observability, dependency, reasoning, critic and reporting responsibilities | Mostly runnable | D1 is orchestrator and hypothesis planner; D3 is observability; D4 covers code, deploy and dependencies; D7 is critic; D8 reports. Reasoning is currently part of D1 rather than an independently packaged role. Decide whether to split it before final submission if the evaluator reads the six named roles literally. |
| Logs, metrics, deployment history, service dependencies and historical incidents | Partial | Bounded log/metric-style records, deployment facts, and D1’s service map are available. Data history is available through D5. A dedicated historical-incident search connector still needs to be added. |
| Structured tool I/O and errors | Partial | Current specialist tools are typed, case-scoped and evidence-backed. Explicit timeout/partial/unavailable simulated responses still need to be implemented and tested. |
| Parallel independent tasks | Runnable | The graph starts D3–D6 branches in parallel when D1 selects them and joins them before one D7 review. |
| Shared state, retries, feedback and termination | Partial | Shared persisted case/evidence/task state and a bounded D7→D1 follow-up loop exist. Production-style timeouts, retries, global budgets and failure recovery remain planned. |
| Ranked causes, support, counterevidence, confidence and actions | Runnable | D8 now returns 1–5 ranked hypotheses with qualitative confidence, supporting IDs, contradicting IDs and missing evidence; D7 reviews the exact draft before delivery. |
| At least 10 varied synthetic incidents | Runnable | Eleven cases are seeded; see [incident catalogue](incident-catalog.md). The current test only checks count and raw-source shape. Add execution assertions and tool-failure cases next. |
| Equal-tools single-agent baseline | Not built | Build a baseline that receives the same complaint, source tools, limits and model; it must not receive hidden answer keys. |
| Compare accuracy, grounding, calls, latency and tokens | Not run | The protocol and result table are in [evaluation-and-results.md](evaluation-and-results.md). Run it only after the baseline and hidden evaluator key exist. |
| Runnable setup and architecture explanation | Runnable | [Setup](setup-and-traced-demo.md), the FastAPI/LangGraph application, and the [architecture page](../research/agent-architecture.html). |
| Technical note of at most 500 words | Ready | [Technical note](technical-note.md). |
| Coding-assistant transcript | Needs manual export | [Transcript note](assistant-transcript.md). Do not manufacture a transcript from summaries. |

## What is deliberately not hardcoded

`app/db/demo_seed.py` contains only scenario title, complaint context and imperfect raw source records. It has no root-cause, expected-report or answer column. The model must query tools and form the report from retrieved evidence. Any hidden answer key used to score accuracy must stay outside the runtime data and must never be passed to an agent.

## Finalisation order

1. Add historical-incident search and structured fault outcomes (`complete`, `empty`, `partial`, `timeout`, `unavailable`).
2. Add ranked-hypothesis/counterevidence/confidence fields to D8 and the persisted report.
3. Build the equal-tools baseline and hidden evaluator key.
4. Run all incidents, fill the results ledger, and add automated assertions.
5. Export and attach the real coding-assistant transcript.
