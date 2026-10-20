# Evaluation research — what existing benchmarks can and cannot establish

Research checked: 2026-10-20. This note concerns evaluation design, not an implementation plan or selected architecture. The assignment remains the controlling specification: at least ten test incidents, misleading/conflicting evidence and tool failures, and a single-agent baseline using the same tools.

## Three complementary references

| Reference | Existing artifact | Useful lesson | Gap relative to this assignment |
| --- | --- | --- | --- |
| AIOpsLab | Live microservice environments, faults, workloads, telemetry, agent interface and evaluators | Evaluate an investigation as interaction with an environment | Running a live cluster is additional complexity for a simulated-data assignment |
| ITBench | IT scenarios, baseline agents, scoring harness and later snapshot tooling | Keep environment, tools, agent and scoring separate | Scenario resolution and diagnosis quality are different metrics |
| RCAEval | Offline telemetry cases and reproducible RCA baselines | Use explicit root-cause labels and ranked localization metrics | Does not itself prove agent collaboration or reliable handling of tool outages |

The table's usefulness/gap judgments are research interpretation. Artifact descriptions are supported below.

## AIOpsLab: environment and evaluation harness

Microsoft's MIT-licensed project deploys applications, injects faults, drives workloads and exposes telemetry to agents. Problems bind an application, task, fault, workload and evaluator; tasks cover detection, localization, analysis and mitigation. The published MLSys 2025 evaluation selects 48 problems, so “48” describes that evaluation rather than every current repository problem. [Repository](https://github.com/microsoft/AIOpsLab), [primary paper](https://yinfangchen.github.io/assets/pdf/aiopslab_mlsys.pdf)

```text
Problem definition -> deploy app + workload + injected fault
                   -> agent/environment interaction trace
                   -> submitted solution + evaluator
                   -> correctness / steps / time / token measures
```

The checked quantitative evaluator counts assistant trace entries as steps and estimates tokens using a fixed tokenizer over trace content. Such estimates need not equal billable model usage, particularly when internal agents, retries or repeated prompt history are absent from the trace. [Quantitative evaluator](https://github.com/microsoft/AIOpsLab/blob/ccf08d0d1d5fa5b30f120e2e8549662d44411b35/aiopslab/orchestrator/evaluators/quantitative.py)

Its qualitative evaluator uses an LLM judge over formatted traces, with a 1–10 reasoning score. This is a distinct kind of evidence from deterministic root-cause matching. [Qualitative evaluator](https://github.com/microsoft/AIOpsLab/blob/ccf08d0d1d5fa5b30f120e2e8549662d44411b35/aiopslab/orchestrator/evaluators/qualitative.py)

## ITBench: scenario success and snapshot replay

The 2025 paper reports a low SRE scenario-resolution rate of 13.8% for its evaluated agents. A newer repository describes snapshot-based diagnosis using ITBench-Lite, a runner, MCP tools and an evaluator producing separate JSON outputs. Read these as different benchmark versions. [Original paper](https://arxiv.org/abs/2502.05352), [replacement agent framework](https://github.com/itbench-hub/ITBench-CISO-SRE-FinOps-Agent)

For a later assignment experiment, fixed telemetry snapshots offer a useful idea: both approaches can receive identical evidence and failure schedules. This does not require adopting the ITBench stack or executing remediation.

## RCAEval: offline telemetry and ranked localization

The RCAEval publication provides nine telemetry datasets with 735 failure cases and 15 reproducible baselines. These cover metric-, trace- and multi-source analysis. The current repository has evolved beyond that publication, so pin a version when reproducing results. [Publication](https://arxiv.org/abs/2412.17015), [repository](https://github.com/phamquiluan/RCAEval)

The checked repository exposes root-cause labels and ranked evaluation, and its license section distinguishes authors' MIT-licensed code/data from bundled baselines with different or missing licenses. Do not assume one repository-level badge licenses every dependency. [Licensing and changelog](https://github.com/phamquiluan/RCAEval#licensing)

This can inspire realistic telemetry shapes and deterministic labels. It cannot replace the assignment's deliberately contradictory observations and tool-failure tests without an explicit adaptation.

## Measurement definitions to discuss before implementation

The following is original evaluation guidance derived from the assignment's requested outputs. It is not a claim that the referenced systems already implement this exact protocol.

| Requested measure | Concrete definition worth agreeing | Common ambiguity to avoid |
| --- | --- | --- |
| Root-cause accuracy | Top-ranked service plus fault mechanism matches hidden ground truth; optionally also report top-k | Counting a symptomatic service as correct because it appears somewhere in a long list |
| Evidence grounding | Fraction of factual report claims supported by valid retrieved evidence; separately score contradictory evidence coverage | Counting a citation as support when its content does not entail the claim |
| Tool-call count | Every attempted call, including failures and retries; also report successful/failed counts | Excluding retries or calls made inside specialist agents |
| Latency | Wall-clock time from incident receipt to final report | Summing parallel task durations or excluding critic/retry/report time |
| Tokens | Sum input/output usage of every model request across roles and repairs | Measuring only the orchestrator or only final-output tokens |
| Inconclusive behavior | Appropriate abstention when required evidence is unavailable; report coverage alongside accuracy | Treating all abstentions as successes or omitting them from the denominator |

For a fair baseline, keep the model, tool implementations, starting information, incident versions and timeout/partial-data schedule fixed. State the resource-budget comparison explicitly: same total budget tests allocation efficiency; each system's natural budget tests practical cost/quality trade-offs. Both can be informative, but they answer different questions.

Ten incidents satisfy the minimum but make each case a ten-percentage-point change in accuracy. Preserve per-incident results and transcripts, and avoid broad significance claims from a single run. A larger later study could repeat runs or add held-out incidents without changing the initial minimum.

## Candidate adversarial incident categories for later discussion

These are research prompts, not a completed dataset: unrelated recent deployment; genuine deployment regression; downstream dependency failure with upstream symptoms; stale historical incident match; contradictory metrics/logs; one telemetry source missing; timeout followed by successful retry; persistent tool failure; partial results that omit decisive evidence; and genuinely insufficient evidence. Hidden labels and failure schedules should remain outside agent-visible observations.

## Coverage required by our expanded system scope

The [current requirements](system-requirements.md) add codebase, actual database contents, infrastructure and AI application behavior to the original research prompts. These categories must be represented in the eventual suite, not merely mentioned in chat:

| Failure family | What the investigator must distinguish |
| --- | --- |
| Missing/incorrect database data | Absent/wrong source record versus a query/filter, cache, transformation or retrieval error |
| Code / deployment / infrastructure | Application logic versus failed rollout, wrong deployed version, resource or connectivity failure |
| Prompt regression | Effective rendered prompt/version differs from an appropriate comparison; no assumption that all bad output is a prompt defect |
| Retrieval/context | Stale index, wrong filter or dropped context versus source data that was already missing |
| Model/tool behavior | Actual model/config/response, tool arguments/results and parsing; successful status does not establish semantic correctness |
| Agent coordination | Wrong routing, dropped/overwritten handoff state, duplicate work, loops, retries or premature termination |
| Unavailable AI history | Cause remains uncertain when the relevant prompt, context or handoff snapshot is absent |

Use vague raw complaints and include AI failures with healthy HTTP/infrastructure metrics. Score discovery of the affected issue, the primary cause, contributing defects and evidence grounding. The baseline needs the same code/data/AI trace tools, not only the original five source families. Fixtures, prompts and run snapshots are agent-visible evidence; root-cause labels remain evaluator-only. This is our evaluation requirement, not a published result from the benchmark systems above.

## Architecture comparison experiments

For the [architecture comparison](architecture.html), evaluate A (supervisor/local task monitors) and D (hypothesis-driven tasks/shared semantic verifier) under the same inputs and tools. Separate the effect of work-selection policy from review policy where feasible; a two-by-two ablation is useful if budget allows. Count all planning/review model calls, not just domain-worker calls. No cost or accuracy advantage for D has yet been established.

## Source ledger and reproducibility status

- [AIOpsLab paper](https://yinfangchen.github.io/assets/pdf/aiopslab_mlsys.pdf), MLSys 2025; [repository](https://github.com/microsoft/AIOpsLab) at checked commit `ccf08d0d1d5fa5b30f120e2e8549662d44411b35`, 2026-09-14. MIT license; code inspected, environment not run.
- [ITBench paper](https://arxiv.org/abs/2502.05352), initially 2025-02-07; [current modular agent repository](https://github.com/itbench-hub/ITBench-CISO-SRE-FinOps-Agent) at `30673b23a7166fc53162b2e6c23a364e7c5f0197`, 2026-03-19. Component/dataset reuse licenses require separate checking.
- [RCAEval paper](https://arxiv.org/abs/2412.17015), initially December 2024, WWW 2025; [repository](https://github.com/phamquiluan/RCAEval) at `259ea4167160256a74ad30004aa3d96a998c846e`, 2026-09-29. Author code/data MIT, imported components vary.

All links accessed 2026-10-20. No benchmark scores in this note were independently reproduced. Do not compare the papers' headline scores directly: tasks, datasets, metrics, tools, models and versions differ.

[Back to research overview](index.html)
