# IBM / ITBench SRE agents — executable tool and evaluation references

Research checked: 2026-10-20. Type: open-source research agents and benchmark infrastructure. Relevance: concrete tools, task limits, diagnosis reports and reproducible evaluation; two versions must be kept distinct.

## Version A: archived CrewAI SRE agent

The original `ITBench-SRE-Agent` repository is archived and directs development to `ITBench-CISO-SRE-FinOps-Agent`. Its code is Apache-2.0. [Archived repository](https://github.com/itbench-hub/ITBench-SRE-Agent)

```text
Active alerts -> diagnosis agent -> diagnosis task / JSON callback
                                 -> remediation task with diagnosis context
                                 -> remediation report
```

At inspected commit `42506dcb77a6ee3f3dbb68bc90836a513485a449`, `crew.py` defines diagnosis/remediation agents, `max_iter=20`, disabled delegation and `Process.sequential`. Diagnosis tools include alerts, kubectl, metrics and traces; later task context references the diagnosis. Optional memory depends on embedding configuration. This is concrete multi-agent code, but its sequential two-role design does not satisfy the assignment's six-role collaboration requirement. [Pinned crew implementation](https://github.com/itbench-hub/ITBench-SRE-Agent/blob/42506dcb77a6ee3f3dbb68bc90836a513485a449/src/lumyn/crew.py)

The diagnosis prompt discusses propagation direction and ambiguous connection exhaustion, encouraging deeper trace/event investigation. Remediation prompts ask for action planning, alert rechecks and revision. Prompt instructions should not be mistaken for independently tested guarantees. [Agent configuration](https://github.com/itbench-hub/ITBench-SRE-Agent/blob/42506dcb77a6ee3f3dbb68bc90836a513485a449/src/lumyn/config/agents.yaml)

## Version B: replacement modular SRE framework

```text
Scenario snapshot -> Zero runner -> Codex CLI -> SRE MCP tools
                         -> agent_output.json -> LLM evaluator
                                               -> evaluation_results.json
```

The replacement README describes a Zero runner, SRE MCP tools and a separate evaluation component. Snapshot data comes from ITBench-Lite. Listed tools cover alerts, Kubernetes events, metric anomalies, trace error trees, topology and Kubernetes specification changes. Its README documents Python 3.12/3.13, containers and a specific CLI compatibility pin; these are repository-specific setup constraints, not general installation advice. [Replacement repository, architecture and prerequisites](https://github.com/itbench-hub/ITBench-CISO-SRE-FinOps-Agent)

The SRE tool documentation is a useful place to study query contracts and temporal/dependency context before building simulated equivalents. [SRE tools documentation](https://github.com/itbench-hub/ITBench-CISO-SRE-FinOps-Agent/blob/main/sre_tools/README.md)

## Results and scope

The original 2025 ITBench paper reports 13.8% SRE scenario resolution. That is a benchmark result under its evaluated agents/models, not the success rate of every current ITBench agent. It measures scenario handling, not just naming a root cause. [Original paper](https://arxiv.org/abs/2502.05352)

## Assignment interpretation

| Requirement | Implication |
| --- | --- |
| Six roles with critic | Neither version is an established drop-in implementation of this requirement. |
| Five tool families | Map events/spec changes/topology into explicit deployment and dependency queries; add historical incidents. |
| Parallel work and shared state | The old sequential crew is evidence that “multiple agents” does not automatically mean parallel collaboration. |
| Recovery from simulated failures | Add controlled timeout/partial-result cases to any later assignment design. |
| Evidence-grounded report | Study report schemas, then ensure ranked hypotheses include contradictions and source pointers. |
| Equal-tools baseline | The replacement's tool separation could help compare orchestration independently of tool capability. |

The assignment asks for corrective recommendations. Real execution of remediation is a separate scope decision and is not required to learn from this reference.

## Availability and limits

Original code and license were inspected; no environment was installed or scenario executed. The replacement root license was not separately verified; check each component and snapshot dataset terms before reuse. Do not combine the archived CrewAI agents, current CLI runner and paper-era scores as if they were one unchanged architecture.

## Source ledger

- [Archived agent repository](https://github.com/itbench-hub/ITBench-SRE-Agent), inspected commit `42506dcb77a6ee3f3dbb68bc90836a513485a449`; accessed 2026-10-20.
- [Replacement repository](https://github.com/itbench-hub/ITBench-CISO-SRE-FinOps-Agent), inspected commit `30673b23a7166fc53162b2e6c23a364e7c5f0197`, dated 2026-03-19; accessed 2026-10-20.
- [ITBench original paper](https://arxiv.org/abs/2502.05352), first submitted 2025-02-07; accessed 2026-10-20. Paper versions differ in overall scenario counts; this note quotes only the scoped SRE result.

[Back to research overview](../index.html)
