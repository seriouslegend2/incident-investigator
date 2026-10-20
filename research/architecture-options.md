# Architecture options: comparison and recommendation

Main artifact: [visual comparison](architecture.html). The [original supervisor simulation](architecture-supervisor.html) is retained as historical option A. This note records research and reasoning behind the current seven-agent direction; no implementation or performance advantage is claimed. Access date: 20 October 2026.

The top-level review's three remaining rules are now specified in the [shared agent protocol](agent-protocol.md): applicability/version checks for late parallel results; material-change invalidation of exact-artifact review; and deterministic incomplete delivery when final review is unavailable. [Separate agent documents](agents/README.md) inherit those rules. [Research reanalysis](agent-contract-research.md) distinguishes primary-source facts from our protocol choices.

## Scaling refinement: preparation and retrieval are not LLM context

The current design targets a multi-repository service estate, not one repository. See [the scale diagram](architecture.html#large-estate) and [full scalable-design contract](scalable-design.md). Prepare indexed source catalogs, repository-qualified code navigation, artifact/source/version bindings and federated telemetry/data/AI adapters before incidents. Investigate progressively: metadata candidates → outcome aggregates → correlated attempt/cohort → related services at their own deployed revisions → source-linked code/data/run slices. Maintain an expandable frontier and a compact case file, not an all-estate prompt or agent per service.

Retrieval can exclude the true cause, so expose candidate/query coverage: D1 can broaden its search and D7 can request a rival source or expanded search. Bound backend scan cost, result pages, context and total investigation work; track freshness/sampling/retention and tenant scope throughout. Missing preparation or evidence produces bounded fallback/clarification or an inconclusive report, not a fabricated route. No load test or billion-line implementation has been completed; prove retrieval recall, resource cost and diagnosis separately using equal-tools baselines.

## Reviewed recommendation: discover the execution path, then test causes

The simple supervisor/expert/critic topology is a sound foundation, not a unique or complete investigation method. Keep the structure, but make its behavior explicit:

- D1 starts from vague text and available source/tool catalogs, not a known correct route. D4 discovers entry points/call sites/event schemas/effective routing; D5 follows relevant data/outbox relationships; D6 follows AI trigger/tool/handoff paths when applicable. D3 corroborates actual candidate attempts using correlated runtime records. Every claimed edge has a source or an uncertainty label; catalogs and runbooks can be stale.
- Keep intended behavior (contracts/tests), implemented behavior (versioned code/config) and observed behavior (runtime/data/provider evidence) distinct. A comparable successful attempt helps locate differences but is not mandatory and does not prove causality. No healthy run means compare against a source-backed expected path, not invent success data.
- Localize a verified divergence or an unknown boundary, then test competing explanations for it. Do not require a complete map or assume all workflows are linear. A local failure point can be downstream of the initiating fault. Provider acceptance, delivery status and customer visibility are distinct claims.
- Assign question/hypothesis tests rather than bulk evidence gathering. Specialists reason within their bounded tasks and flag unexpected leads. D1 owns both cross-source hypothesis comparison and selected work/compact state; D7 independently challenges causal claims with original-source access and authority to request rival checks; D8 writes the reviewed report.
- Preserve evidence provenance and revision history; invalidate interpretations and reconsider dependent claims when new evidence contradicts them. D7 review is not a correctness guarantee. Missing/partial telemetry remains unknown; repeated summaries are not independent evidence.
- Use scoped read-only tools, privacy/secret controls, untrusted-content boundaries, bounded recovery/stopping and explicit inconclusive outcomes. Test investigator failures as well as application failures. No autonomous production remediation.

**Current decision: D2 is removed.** D1 performs hypothesis comparison, cross-source synthesis and distinguishing-test selection in addition to orchestration. D7 remains an independent challenger, not the main analyst reviewing its own work. The user explicitly chose responsibility-based architecture rather than a separate agent for each assignment role. The PDF still names a Reasoning Agent; accurately document that its responsibility is merged into D1, rather than inventing wording that makes the role list optional. Retain existing IDs for the remaining seven agents; do not reintroduce an analyst through the scale design, a diagram or a hidden tool call.

**Question-generation correction:** D1 must not be shown naming a wrong field or stale cache before learning the relevant implementation. Start with an observed stage, ask D4/D6 to explain its source-backed behavior and dependencies, then issue specific code/data/runtime tests. General engineering possibilities are explicitly exploratory, not established architecture. Each decision retains premises, unknowns and why the question is justified. D7 audits the investigation's unsupported premises and missing checks as well as its final explanation. This is a proposed contract with [planned acceptance tests](question-grounding.md), not implemented hallucination prevention.

The HTML now starts with a [source-discovery explanation](architecture.html#discover-the-path), [expected/healthy/failed comparison](architecture.html#expected-vs-observed), and ten-step agent conversation. W1/W2 represent illustrative expected-route and healthy-attempt sources; E1–E5 represent failed-attempt, versioned-code and time-matched data evidence. All scenario values are invented teaching examples, not a running investigator or hardcoded implementation answers.

This refinement is our synthesis. Resolve documents focused investigators and independent verification; incident.io documents revisable cited findings and time-frozen backtesting; Datadog documents targeted hypothesis tests. These sources do not establish the exact role split or prove this proposal beats the basic supervisor. Coverage must be shown through cases including queues, caches/replicas, external/customer boundaries, AI coordination, multiple faults and absent evidence—not by adding more agent boxes.

## Options and evidence

| Option | Control model | Useful property | Limitation for this task |
| --- | --- | --- | --- |
| A: user's supervisor + local monitors | A lead selects experts and follow-ups; each task has a local checker; a final critic reviews the report | Clear task ownership and feedback | Lead reasoning can anchor; repeated semantic review can add cost. Those risks depend on implementation, not just topology. |
| B: fixed outer workflow | Stage order is predefined; adaptive reasoning, fan-out and retries can exist inside stages | Predictable execution and testing | Novel cross-stage investigations need supported transitions. A mere prompt chain would not satisfy the assignment. |
| C: peer handoffs | The active specialist transfers control to a peer | Expertise can change dynamically | Basic handoff is sequential; parallel investigation and global ownership require additional machinery. |
| D: proposed hypothesis-driven task graph | D1 compares causes and chooses discriminating questions; code dispatches ready tasks; results revise a shared board | Explicit competing causes, dependencies and review status | More state and selection policy; a poorly chosen question can still miss the cause. No advantage has been measured. |

Judgments above are our analysis, not benchmark results or complete descriptions of proprietary systems.

Anthropic's pattern article distinguishes predefined workflows from dynamic agents and describes orchestrator-workers and evaluator-optimizer loops. These support the structural comparison, not a claim that every specialist needs a monitor. Its later Research engineering account describes a lead spawning parallel workers and adapting as findings arrive; it also discusses coordination and token costs. Research-system performance figures cannot be transplanted to incident diagnosis. [Pattern article](https://www.anthropic.com/engineering/building-effective-agents), [built research system](https://www.anthropic.com/engineering/multi-agent-research-system)

Magentic-One is an implemented generalist system with a task ledger for facts/guesses/plan and a progress ledger for assignments and progress. It replans when progress stalls. This supports explicit planning state, but it is not an incident-specific architecture or evidence of our proposed local checker arrangement. [Microsoft Research](https://www.microsoft.com/en-us/research/articles/magentic-one-a-generalist-multi-agent-system-for-solving-complex-tasks/)

Uber's supplied presentation describes fixed outer stages, deterministic collection, adaptive RCA queries, parallel specialists and bounded validation. It must not be portrayed as a one-pass collection chain. The visualization adapts the workflow pattern to our scope; Uber also repairs code, which exceeds the assignment. [Existing case note](systems/uber-debug-assist.md), [supplied transcript](../uberassist/uberassist_youtube_transcript.txt)

LangGraph Swarm implements handoff tools and a shared conversation state. Microsoft's pattern guide says ordinary handoff transfers control, generally one active agent at a time, and distinguishes it from concurrent orchestration. Thus peer handoff alone does not establish the required parallel execution. [Official repository](https://github.com/langchain-ai/langgraph-swarm-py), [Microsoft pattern guide](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns#handoff-orchestration)

Datadog describes proposing hypotheses, validating/rejecting them through targeted telemetry, and drilling into supported branches. incident.io describes cited findings that can be canceled by contradictory evidence and an adversarial review loop. These inform D's evidence/hypothesis links and revisable state. Neither publishes D's exact scheduler or claim-promotion policy. [Datadog](https://www.datadoghq.com/blog/building-bits-ai-sre/), [incident.io](https://incident.io/blog/building-investigations-what-it-takes-to-build-an-ai-sre)

Resolve's retrospective describes focused parallel investigators, independent verifiers and shared evidence, and reports failure modes of rigid workflows and saturated primary-agent contexts. It is relevant motivation, not proof that D beats A. [Resolve](https://resolve.ai/blog/Failures-That-Led-to-2x-Agent-Accuracy-Improvement)

## My recommended design: D

The HTML uses seven active names: **D1** Investigation lead (reasoning + orchestration); **D3** Observability; **D4** Code/change/infrastructure; **D5** Database/data/dependencies; **D6** AI behavior; **D7** Verifier/critic; **D8** Report writer. **R1** is the code scheduler/supervisor, **R2** the investigation store, and **R3** code validation. R components are not LLM agents. D7 performs claim review and final-report review as separate invocations with fresh context, rather than adding two new roles. All invocations pass through R1 and output validation through R3, even where diagrams abbreviate these hops.

The [D tab](architecture.html#option-d) has a seven-agent input/output roster, a detailed named-node diagram and an eleven-step example including D1's internal reasoning updates. From a vague order-assistant complaint, discovery identifies a candidate run, D1 compares missing-data/wrong-query/lost-handoff hypotheses, D5 checks source records, D6 checks actual tool/handoff traces, and D4 checks code/version history. D7's report review sends D1 back to D4 for a missing deployment binding before D8 revises and D1 delivers the reviewed artifact. D3 remains unused in that path. Source IDs E1–E6 and review states are retained throughout; the values are illustrative fixtures, not a live diagnosis.

Keep the user's dynamic delegation, specialists-as-tools, bounded retries and final critic. Make the control policy explicit:

1. Discovery establishes candidate issue scope from vague text; no hidden service/time hint is provided.
2. A shared board stores raw source references, provisional/reviewed claims, competing hypotheses, contradictions, unknowns and questions.
3. D1 maintains competing causes and chooses observations that would distinguish them, using evidence availability, cost and remaining budget. It performs reasoning and prioritization as one lead role, not calls to another analyst. This can be a documented heuristic; no numerical information-gain estimator is presumed.
4. A code scheduler runs ready tasks with explicit prerequisites, scopes and budgets. Independent tasks can run concurrently. Each selected domain specialist reasons and queries within its task, rather than merely fetching one source.
5. All outputs receive code validation. New claims used to rank causal hypotheses, conflicts and questionable support receive separate semantic review. Unreviewed claims remain provisional and cannot be promoted into final conclusions merely because a source ID exists.
6. Checked evidence updates can weaken a hypothesis, invalidate a finding or create a new task. Replanning responds to meaningful evidence, conflicts and stalls; it need not invoke a lead model on every routine tool response.
7. The writer and independent final critic evaluate the exact report, alternatives, uncertainty and recommendations. Delivery uses the reviewed artifact. Budgets, missing evidence or unresolved scope can produce a limited/inconclusive result.

This is a research-informed synthesis, not a claim of a novel invention or a production architecture. A can incorporate these ideas too. D specifies the hypothesis/task/review state and event-driven scheduling more tightly than the user's original supervisor diagram; it does not require a different roster of specialist roles.

## Monitor trade-off

In A, the task-level monitor is associated with a specialist invocation. In D, code validation still runs for every result, while a shared semantic verifier checks claims at causal promotion or conflict. This can avoid reviewing the same routine observation repeatedly, but adds claim-status and invalidation logic. All final causal claims still undergo report review. Reuse checked findings only when scope and source versions remain valid.

We do not know whether D will be cheaper or more accurate. Conditional review can miss a bad claim if eligibility policy is weak; pervasive review can be expensive and still share model biases. A checker is not a ground-truth oracle. Compare both policies explicitly.

## Decision rule

Run A and D against the same at-least-ten incidents and required single-agent baseline, with equal tools, model, initial messages, source records, clarification policy, replayed failures and comparable documented budgets. Report accuracy, grounding, attempted tool calls, latency and all-model tokens; separately count planning/review calls. Include code/data/AI/infrastructure faults and misleading or missing evidence. Test hypothesis/task control and review policy separately where feasible, so effects are not confounded.

Choose D only if the diagnosis/grounding benefit or resource efficiency justifies its bookkeeping. If it does not, A is the simpler fallback. Framework and exact budgets remain undecided.

## Source dates and verification limits

- Anthropic pattern article: 19 December 2024; Research engineering account: 13 June 2025. Live articles may include later tooling edits; pattern observations here do not assert a historical SDK version.
- Magentic-One: Microsoft Research public architecture account; article/code not executed here. Publication date not needed for the comparison.
- Uber: supplied transcript/slides, with source provenance in the case note.
- Datadog: 12 January 2026; incident.io: 1 October 2026; Resolve: live body 26 June 2026, with the previously noted indexed-date inconsistency.
- Microsoft orchestration guide and Swarm repository: live documentation/source, accessed 20 October 2026. No exact installed library behavior or version is assumed.

All architecture cost/quality trade-offs are reasoned expectations. No architecture in this comparison was implemented, installed or benchmarked during this update.
