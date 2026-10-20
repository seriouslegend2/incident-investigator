# Datadog — Bits Investigation (formerly Bits AI SRE)

Research date: 2026-10-20. Category: commercial production product. Relevance: **very high for evidence-driven investigation and evaluation; incomplete evidence for the assignment's exact agent decomposition**. This is a study of the shipped product, not a recommendation to reproduce its complete architecture.

## What exists, and what problem it solves

Datadog's product announcement states general availability and reports production use by thousands of organizations. Alerts trigger an autonomous investigation using monitor context, runbooks, previous investigations, and telemetry. Hypotheses can be validated, invalidated, or inconclusive. Engineers can request additional analysis and correct conclusions. These are vendor descriptions, not independently reproduced results. [D1](https://www.datadoghq.com/blog/bits-ai-sre/)

Current operating documentation explicitly permits a final inconclusive outcome when evidence cannot support a defensible conclusion. This is unusually close to the assignment's requirement to investigate incomplete data without forcing an answer. [D4](https://docs.datadoghq.com/bits_ai/bits_investigation/investigate_issues/?lang_pref=en)

## Publicly documented architecture

The following flow is a simplified reconstruction of the published investigation strategy, not a leaked internal component diagram. [D2](https://www.datadoghq.com/blog/building-bits-ai-sre/)

```text
Incident / monitor alert
  → gather initial context
  → propose hypotheses
  → targeted telemetry queries for each hypothesis
  → reject unsupported branches; deepen promising branches
  → repeat
  → evidence-backed root cause analysis
```

The engineering article documents a Kafka incident where an earlier implementation made 12 tool calls and retrieved the decisive commit-latency signal but selected unrelated application errors as the cause. Targeting evidence to individual hypotheses corrected that failure. Its benchmark uses real incidents, ground truth labels, and LLM grading aligned to human judgments. [D2](https://www.datadoghq.com/blog/building-bits-ai-sre/)

The product article additionally describes parallel hypothesis exploration and tools for logs, traces, metrics, recent changes, and Kubernetes events. This establishes parallel investigation behavior; it does **not** disclose six separate agents or an independently implemented Critic Agent. [D1](https://www.datadoghq.com/blog/bits-ai-sre/)

## Tools, state, and feedback

Documentation describes an observation/reasoning/action loop that refines hypotheses as new telemetry arrives. Its data-source section is the appropriate place to check integration coverage. Treat the exact function schemas, internal message protocol, and storage engine as undisclosed. [D4](https://docs.datadoghq.com/bits_ai/bits_investigation/investigate_issues/?lang_pref=en)

The assignment's five simulated tool families should remain separate questions during design review: logs, metrics, deployments, dependencies, and incident history. Do not conclude that a vendor supports a particular tool contract simply because it supports the underlying data type.

## Evaluation and reliability evidence

Datadog's evaluation platform packages each scenario as hidden root-cause ground truth plus an isolated world snapshot. It preserves irrelevant neighboring signals to avoid unrealistically easy tests. Adding realistic noise reportedly reduced pass rate by roughly 11% and forced removal of 35% of early labels. It tracks per-scenario results, segments by domain, and runs full evaluations weekly. These are **vendor-reported internal results**, not a public leaderboard. [D3](https://www.datadoghq.com/blog/engineering/bits-ai-eval-platform/)

The same source warns that correct individual tools do not guarantee correct tool chaining. It evaluates investigation trajectory as well as conclusions. It does not supply a public equal-tools, single-agent experiment with all five assignment metrics. [D3](https://www.datadoghq.com/blog/engineering/bits-ai-eval-platform/)

## Direct assignment mapping and questions to retain

| Assignment requirement | Research assessment |
| --- | --- |
| Genuine collaboration | Parallel hypothesis exploration is documented; distinct agent boundaries remain undisclosed. |
| Critic and re-investigation | Validation and branch rejection are relevant; an independent critic is unverified. |
| Shared investigation state | Iterative findings exist; concurrency protocol and state schema are unverified. |
| Evidence and uncertainty | Strong match: hypothesis statuses and an explicitly inconclusive final result. |
| Failure recovery and limits | Public sources reviewed do not establish retry counts, timeout policy, or token budgets. These must be specified independently. |
| Ten synthetic incidents and baseline | Evaluation infrastructure is a useful reference; our assignment still requires its own dataset, baseline, and measurements. |

Possible experiments, **our analysis rather than Datadog claims**: include an incident where the correct evidence appears early but is surrounded by more alarming irrelevant errors; test whether each hypothesis cites both supporting and disconfirming observations; keep ground truth inaccessible to both baseline and multi-agent runs. Evaluate useful early evidence separately from completed RCA latency.

## Source ledger

All sources are first-party. Accessed **2026-10-20**. Live documentation may change; no page-specific update date is asserted when absent.

| ID | Source and direct link | Publication / update | Used for |
| --- | --- | --- | --- |
| D1 | [Introducing Bits Investigation, your AI on-call teammate](https://www.datadoghq.com/blog/bits-ai-sre/) | Published 2025-06-10; visible update 2025-12-02 | Availability, production usage, parallel hypotheses, statuses, feedback |
| D2 | [How we built an AI SRE agent that investigates like a team of engineers](https://www.datadoghq.com/blog/building-bits-ai-sre/) | 2026-01-12; separate update not shown | Branching investigation, Kafka failure example, benchmark method |
| D3 | [How we built a real-world evaluation platform for autonomous SRE agents at scale](https://www.datadoghq.com/blog/engineering/bits-ai-eval-platform/) | 2026-04-07; separate update not shown | Noisy snapshots, hidden labels, regression detection |
| D4 | [Investigate Issues](https://docs.datadoghq.com/bits_ai/bits_investigation/investigate_issues/?lang_pref=en) | Undated live documentation | Operating loop and final inconclusive behavior |

Evidence boundary: no source code or independent reproduction of this proprietary system was reviewed. Product adoption and performance figures remain vendor claims.
