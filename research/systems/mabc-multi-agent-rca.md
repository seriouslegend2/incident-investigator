# mABC — seven collaborating RCA agents, with an important code caveat

Research checked: 2026-10-20. Type: published research prototype with public Python code. Relevance: one of the closest role-level matches to the assignment, but the checked code does not establish all paper claims.

## Documented architecture

```text
Alert Receiver -> Process Scheduler
                    |-> Data Detective
                    |-> Dependency Explorer
                    |-> Probability Oracle
                    |-> Fault Mapper / fault web
                    -> further subtasks until diagnosis
                    -> Solution Engineer
All agents: paper describes a challenge/voting mechanism
```

The paper describes seven specialist agents, tool-driven ReAct or direct responses, iterative subtask generation, a fault web and weighted voting. It states a 20-step termination limit and evaluates on Train-Ticket and AIOps Challenge data. “Abstain” is an agent's voting choice; it is not necessarily a final inconclusive incident report. [Paper, sections 2–4](https://arxiv.org/html/2404.12135v3)

## Critical distinction: paper architecture versus inspected implementation

At checked repository commit `79272cea7e59202f530495d17e8f6327a31cb545`, the ReAct runner's `eval_and_run_one_step` has the call to the voting evaluator commented out and sets `result = True`. The recursive `run` method does not visibly enforce the paper's 20-step cap. These are findings about this code path, not a claim that every possible experimental version lacks these features. [Pinned runner source](https://github.com/zwpride/mABC/blob/79272cea7e59202f530495d17e8f6327a31cb545/agents/base/run.py)

The entry point instantiates seven agents and a scheduler, then invokes a Solution Engineer. It expects local label data and includes a five-case loop break; it is not a ready-made evaluation of the assignment's ten adversarial incidents. [Pinned entry point](https://github.com/zwpride/mABC/blob/79272cea7e59202f530495d17e8f6327a31cb545/main/main.py)

## Availability and measured claims

The public repository provides agent/tool files, sample data and run instructions, under Apache-2.0. The README asks users to adapt their data to the sample format. Code presence establishes a research artifact, not successful local execution or operational reliability. [Repository and license](https://github.com/zwpride/mABC)

The paper compares mABC with ReAct and ablates workflow, multi-agent behavior and voting. However, the inspected arXiv HTML's main table and explanatory prose disagree on the overall average (46.9 versus 64.9). Do not repeat either as a settled headline without reconciling the final PDF/version and experimental configuration. [Table 4 and section 3.5](https://arxiv.org/html/2404.12135v3)

## Assignment mapping and questions

| Assignment concern | What to take into the later architecture discussion |
| --- | --- |
| Orchestrator / observability / dependency roles | Compare explicit role contracts with the scheduler and specialists. |
| Dedicated critic | A challenge vote and an independent evidence-auditing role are different designs. |
| Shared state | Ask whether the fault web preserves source IDs, time ranges and contradictions. |
| Parallel independent tasks | Verify actual concurrent execution; a list of agents alone does not demonstrate it. |
| Bounded loops and recovery | Require executable enforcement and failure tests, given the paper/code discrepancy. |
| Confidence | A node probability or vote weight needs calibration before being reported as incident confidence. |
| Inconclusive outcome | Define an incident-level insufficient-evidence result separately from vote abstention. |

Agreement should be evaluated against evidence and ground truth. Increasing an agent's voting weight for agreeing with the group could otherwise reward consensus rather than factual accuracy; that is an analytical concern to test, not a measured failure result.

## Source ledger

- [Final publication record, Findings of EMNLP 2024](https://aclanthology.org/2024.findings-emnlp.232/), November 2024; accessed 2026-10-20.
- [Primary paper, arXiv version 3](https://arxiv.org/html/2404.12135v3), 2024 research; accessed 2026-10-20. Detailed architecture and experimental claims.
- [Author repository](https://github.com/zwpride/mABC), inspected snapshot `79272cea7e59202f530495d17e8f6327a31cb545`; accessed 2026-10-20. Code was inspected, not executed.

[Back to research overview](../index.html)
