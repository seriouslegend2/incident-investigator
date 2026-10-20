# Meta — DrP investigation platform

Research date: **2026-10-20**. Relevance: **very high for reliable investigation execution**, although the published platform is not a six-agent LLM implementation. Status: an internal system deployed for years; public architecture and research paper, with no runnable public DrP repository verified here.

## Established system and scale

DrP turns expert playbooks into code-based analyzers. The official account describes typed inputs, reusable analysis libraries, chained dependency investigations, structured findings, workflow integrations, and post-processing. At publication Meta reports **300+ teams, 2,000+ analyzers, and about 50,000 analyses daily**. These are analyzer runs, not necessarily unique incidents. [Meta engineering article, December 19, 2025](https://engineering.fb.com/2025/12/19/data-infrastructure/drp-metas-root-cause-analysis-platform-at-scale/).

The paper describes a request queue, workers and isolated execution; a context container and structured findings; bounded retries and timeouts; persisted results and execution logging; and distributed execution of parallel analyzer DAGs. Dependency analyzers exchange context and results. Historical-run backtesting and canaries catch analyzer regressions. Stateful post-processors are not retried on failure because of duplicate-side-effect risk. The paper reports roughly **20% average MTTR improvement**, with some teams above 80%; its observational production comparisons do not establish an LLM-agent accuracy gain. [Paper, December 3, 2025](https://arxiv.org/html/2512.04250v1).

```text
Alert / incident tool / UI / CLI
               |
        request + context
               |
        persistent queue
               |
      worker -> isolated analyzer
                     |
              dependency analyzers / DAG
                     |
         structured findings + stored result
                     |
        responder view / post-processing tier
```

This is a conceptual reconstruction, not a verbatim production diagram. Publication-specific architectural details are in paper §§4–6. The official article describes AI-native evolution as future work; multiple code analyzers should not be relabeled as multiple LLM agents. [Official article](https://engineering.fb.com/2025/12/19/data-infrastructure/drp-metas-root-cause-analysis-platform-at-scale/), [paper](https://arxiv.org/html/2512.04250v1).

## Assignment mapping and interpretation

| Assignment concern | Why this precedent is useful |
|---|---|
| Shared state and structured communication | A common context/result contract makes a dependency investigation composable. The assignment can use that idea without adopting Meta's runtime. |
| Parallelism and task dependencies | A DAG distinguishes independent work from tasks needing earlier results. Concurrency alone does not provide useful collaboration. |
| Tool failures and recovery | Retry count, timeout, and final failure state should be explicit and observable. An exhausted retry budget must not silently become “no evidence.” |
| Evidence-backed reporting | Machine-readable findings make it possible to validate whether report claims reference actual observations. |
| Feedback and maintenance | Replaying investigation inputs after a change can reveal broken coordination and failure handling. Dataset replay should remain separate from fitting answers to individual incidents. |
| Equal-tools baseline | Reliability mechanisms can affect both diagnosis quality and latency. The baseline needs comparable tool semantics so the evaluation isolates coordination. |

These are our interpretations for later discussion, not evidence that DrP implements the assignment's required roles or hypothesis protocol.

## Lessons and open questions

The most useful lesson is that an investigator is also an executing program: it needs clear state transitions, dependable inputs, and bounded resource use. A prototype can model these with small components; large-scale queues, binary packaging, and production fleets are not prerequisites.

DrP does not establish the assignment's named reasoning/critic/reporting agents, competing natural-language causal hypotheses, explicit contradiction tracking, LLM confidence calibration, token budgets, or a same-tools single-agent comparison. Its production MTTR findings should therefore motivate operational discipline, not serve as an expected score for our synthetic incidents.

## Source ledger

- **Primary engineering account:** [DrP: Meta's Root Cause Analysis Platform at Scale](https://engineering.fb.com/2025/12/19/data-infrastructure/drp-metas-root-cause-analysis-platform-at-scale/), **2025-12-19**; accessed **2026-10-20**.
- **Primary paper:** [DrP: Meta's Efficient Investigations Platform at Scale](https://arxiv.org/abs/2512.04250), v1 **2025-12-03**; [full HTML](https://arxiv.org/html/2512.04250v1); accessed **2026-10-20**. Sections 4–6 cover contracts/execution, §7 evaluates adoption and MTTR, and §7.2.5 discusses methodological limitations.
