# Research pack: production incident investigation systems

Prepared on 20 October 2026 after reading the full assignment. Scope: research existing built systems before deciding our architecture.

## Open this first

Open [index.html](index.html) in a browser. It is the concise, self-contained explanation: assignment, inputs, expected behavior, deliverables, and the most useful lessons from existing systems. This is the main reading file.

For the implementation decision, open [implementation-plan.html](implementation-plan.html). It is the single visual end-to-end build plan: what the user inputs, where the control plane/LLM runner/private gateway/source systems live, each role’s allowed inputs/tools/outputs, the D4→D5 code-to-data handoff, a complete example, onboarding, security gates, KookarCore reuse boundaries and phased acceptance criteria. [implementation-plan.md](implementation-plan.md) is the complete companion checklist.

The implementation is in [../incident-investigator/README.md](../incident-investigator/README.md). It is replacing the discarded fixture-only prototype with individual KookarCore-style agent packages, live OpenAI tool-calling turns, a Postgres/Supabase migration, seeded demo sources and LangSmith trace configuration. It needs runtime keys and a demo database before a live run; no canned conclusion fallback exists.

For the latest work, open [how the agents actually run](architecture.html#runtime-contracts): where code/read replicas/logs/deployments live; the real backend tool loop; exact inputs/results for 41 tools; and a code-to-data handoff that gives D5 the lookup context. Then use the [agent-contract overview](architecture.html#agent-contracts) for seven separate documents with precise role inputs, tool tables and structured outputs. [Full JSON fixtures and schemas](contracts/README.md) are optional implementation detail. [Shared protocol](agent-protocol.md) specifies late-result applicability, revocable exact-report approval and deterministic incomplete status on reviewer failure. [Research reanalysis](agent-contract-research.md) records checked primary sources and design limitations.

The architecture now begins with the [large-estate design](architecture.html#large-estate): prepare source/repository/deployment indexes, narrow before model reasoning, traverse relevant multi-repository boundaries and retain worst-case limits. [scalable-design.md](scalable-design.md) contains source/tool contracts and the proposed load/coverage tests. This is a design update, not a runnable or billion-line-tested implementation.

The [question-origin explanation](architecture.html#grounded-questions) corrects the earlier skipped discovery step: D1 learns relevant implementation from specialists before asking source-specific questions. [question-grounding.md](question-grounding.md) defines premise/unknown tracking, self-checks, independent review and tests for the investigator's own hallucinations/omissions. These are design requirements and planned tests, not an implemented guarantee.

For the architecture discussion, [architecture.html](architecture.html) starts with the runtime/source-location explanation and individual contracts, followed by the scale design and **“Messages are not reaching the customer group”** walkthrough. It shows how D1 discovers rather than assumes the path, with expected/healthy/failed comparisons. A successful run is helpful but not required; the localized failure still needs causal investigation. Ten events show D1's decisions, agent inputs/outputs, parallel checks, repeat calls, critic feedback and the final answer. All findings are illustrative. The collapsed A–D comparisons and [historical supervisor simulation](architecture-supervisor.html) are background, not additional active roles.

The current design has **seven agents: D1, D3, D4, D5, D6, D7 and D8**. D2 is removed; D1 owns reasoning and orchestration, while D7 independently challenges it. Existing IDs are preserved to avoid renaming the specialists. Start with the [customer-group agent conversation](architecture.html#customer-group-example). For optional implementation detail, open [option D](architecture.html#option-d): R1–R3 identify ordinary software, and an eleven-step AI example shows payloads, D1's internal hypothesis updates and critic feedback. Use **Next step** or the step selector there. The original supervisor simulation is historical background, not the current role split.

The current scope is also recorded in [system-requirements.md](system-requirements.md): a vague complaint starts discovery across code, deployment/infrastructure, database contents, config/env, and AI behavior. AI coverage explicitly includes prompts, model settings, retrieval context, tool results, agent handoffs, shared state, and coordination failures. The candidate architecture now includes an AI behavior investigator; its exact role split remains a proposal.

The earlier detailed archive is [detailed-research.html](detailed-research.html). It is optional background; reading it is not needed to understand the guide.

Suggested reading: [assignment requirements](assignment-reading.md), [Uber Debug Assist](systems/uber-debug-assist.md), [comparison](comparison.md), [evaluation research](evaluation-landscape.md), then [architecture discussion questions](next-discussion.md).

## Guides and synthesis

| File | Contents |
| --- | --- |
| [runtime-and-tools.md](runtime-and-tools.md) | Physical source locations, backend/model/tool loop, trusted credentials, code-to-data handoff and replica safety |
| [implementation-plan.html](implementation-plan.html) | **Final implementation view:** source-based KookarCore reuse, private evidence gateway, source connections, role flow, rollout and readiness gates |
| [implementation-plan.md](implementation-plan.md) | Full engineering/onboarding/test plan behind the visual implementation page |
| [tool-catalog.md](tool-catalog.md) | All 41 proposed tools: agent eligibility, actual queried backend, exact input/output fields, failure semantics and guards |
| [contracts/README.md](contracts/README.md) | Strict JSON schemas and seven complete Task/AgentAnswer/Result examples, contract build and offline validation |
| [system-requirements.md](system-requirements.md) | Current product scope, required evidence, AI behavior investigation, proposed owners and evaluation coverage |
| [architecture-options.md](architecture-options.md) | Research-backed architecture comparison, distinct recommendation, monitor trade-off and evaluation decision rule |
| [scalable-design.md](scalable-design.md) | Multi-repository scale design, indexed retrieval, deployment provenance, bounded query contracts, failure limits and validation plan |
| [question-grounding.md](question-grounding.md) | How questions follow available knowledge, unsupported-premise checks, investigator self-audit and planned acceptance tests |
| [agents/README.md](agents/README.md) | Overview and links to the seven individual agent contracts |
| [agent-protocol.md](agent-protocol.md) | Common Task/Result interface, bootstrap access, late-result handling, version-bound approval, delivery and stopping |
| [agent-contract-research.md](agent-contract-research.md) | Primary-source recheck, agent-boundary decisions, lifecycle reanalysis and implementation unknowns |
| [assignment-reading.md](assignment-reading.md) | Full requirement map, deliverables, constraints, and six-role ambiguity |
| [comparison.md](comparison.md) | Eleven system studies compared against the assignment; useful patterns and trade-offs |
| [evaluation-landscape.md](evaluation-landscape.md) | AIOpsLab, ITBench, RCAEval, measurement definitions, and candidate adversarial scenarios |
| [research-method.md](research-method.md) | Source standards, evidence labels, verification limits, and packaging |
| [next-discussion.md](next-discussion.md) | Questions to decide together after the research |

## Existing systems

| File | Focus |
| --- | --- |
| [systems/uber-debug-assist.md](systems/uber-debug-assist.md) | Uber's investigation harness, parallel specialists, controls, presentation evidence, and metric caveats |
| [systems/incident-io-investigations.md](systems/incident-io-investigations.md) | Parallel evidence checks, adversarial critic, revisable findings |
| [systems/resolve-ai.md](systems/resolve-ai.md) | Hypothesis specialists, independent verifier, shared evidence, API contracts |
| [systems/datadog-bits-investigation.md](systems/datadog-bits-investigation.md) | Hypothesis trees, inconclusive outcomes, noisy evaluation snapshots |
| [systems/holmesgpt.md](systems/holmesgpt.md) | Open-source tool loop, structured failures, context management, evaluation |
| [systems/meta-ai-rca.md](systems/meta-ai-rca.md) | Retrieval and ranking of likely culprit code changes |
| [systems/meta-drp.md](systems/meta-drp.md) | Investigation execution, shared context, dependency DAGs and recovery |
| [systems/microsoft-rcacopilot.md](systems/microsoft-rcacopilot.md) | Diagnostic workflows and historical incident retrieval |
| [systems/alibaba-rcagent.md](systems/alibaba-rcagent.md) | Controller/expert agents, evidence snapshots, invalid-action feedback |
| [systems/mabc-multi-agent-rca.md](systems/mabc-multi-agent-rca.md) | Seven-agent research architecture and checked paper/code discrepancies |
| [systems/ibm-itbench-sre-agent.md](systems/ibm-itbench-sre-agent.md) | Archived and replacement implementations, tools, schemas and evaluation |

Each system note explains what already exists, its documented architecture, source/data flow, relevance to the assignment, reported results where available, and undisclosed details. Availability, claims, inference, and independently inspected code are distinguished.

## Original materials and build

- [Assignment PDF](../Orange%20Invest%20Assignment%20FE%20%281%29.pdf)
- [Supplied Uber talk transcript](../uberassist/uberassist_youtube_transcript.txt)
- [Uber pipeline screenshot](../uberassist/uberassist.png)
- [Uber productionization screenshot](../uberassist/uberassist1.png)
- [HTML generation script](build-overview.mjs)

To refresh schemas/tool catalog after changing their definitions: run `node research/contracts/build-contracts.mjs`, then `python research/contracts/validate-contracts.py`. The latter checks contracts, not agent behavior. Refresh the optional detailed archive with `node research/build-overview.mjs`. The concise guide at `index.html` and overview at `architecture.html` are maintained separately. No application integration or benchmark execution is included in this phase.
