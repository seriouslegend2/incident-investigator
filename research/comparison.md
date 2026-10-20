# Comparison: which existing systems answer which assignment questions?

Research date: 20 October 2026. This is a synthesis of the linked case studies, not a proposed architecture. “Documented” means the cited source describes a behavior; it does not mean we independently tested the production system.

For our current product scope, use [system-requirements.md](system-requirements.md) or the [main HTML guide](index.html). They explicitly include vague-report discovery, codebase, database contents, deployment/infrastructure, config/env, and AI application prompt/model/retrieval/tool/handoff/coordination failures. The case comparison below is research evidence, not a limit on that scope. Langfuse tracing and prompt-to-run links provide additional first-party evidence for the AI observability layer, cited in the current requirements.

Architecture choices are compared separately in the [visual architecture comparison](architecture.html) and [decision notes](architecture-options.md): the user's supervisor/local-monitor proposal, fixed outer stages, peer handoffs, and a recommended hypothesis-driven task graph. The recommendation is design analysis, not a published result or a final decision.

## Most useful reading order

Start with [Uber Debug Assist](systems/uber-debug-assist.md) for a concrete investigation harness. Read [incident.io](systems/incident-io-investigations.md) and [Resolve AI](systems/resolve-ai.md) for agents challenging other agents' conclusions. Then study [Datadog](systems/datadog-bits-investigation.md) for hypothesis testing and noisy evaluation, [Meta DrP](systems/meta-drp.md) for execution reliability, and [HolmesGPT](systems/holmesgpt.md) for inspectable tool-loop code. [mABC](systems/mabc-multi-agent-rca.md) is a close research match to the requested roles, with important implementation caveats.

## System landscape

Each system name links to architecture details, direct primary sources, results, and limitations. Judgments in the last two columns are our interpretation of that evidence.

| Existing system | What is built / evidence available | Strongest assignment connection | What it does not establish |
| --- | --- | --- | --- |
| [Uber Debug Assist](systems/uber-debug-assist.md) | Internal system described by its engineer; supplied talk and slides, online corroboration | Deterministic harness, parallel RCA specialists, state transfer, scoped inputs and turn limits | Independent critic, ranked competing hypotheses, formal abstention, equal-tools baseline |
| [incident.io Investigations](systems/incident-io-investigations.md) | Commercial product; public engineering account and changelogs | Parallel checks, cited findings that can be superseded, adversarial critic and reinvestigation | Complete agent exchange schemas, retry policy, global budgets |
| [Resolve AI](systems/resolve-ai.md) | Commercial deployment descriptions; engineering retrospective and API docs | Focused hypothesis investigators, independent verifiers, shared evidence | Reproducible internal comparison, calibrated confidence, all failure-recovery details |
| [Datadog Bits Investigation](systems/datadog-bits-investigation.md) | Commercial product; engineering and operating documentation | Hypothesis branches, targeted telemetry, inconclusive outcomes, realistic evaluation snapshots | Exact agent decomposition and an independently implemented critic |
| [HolmesGPT](systems/holmesgpt.md) | Open-source agent; pinned code and versioned docs | Structured errors, query concurrency, provenance and context management | Six collaborating roles or mandatory counterevidence handling |
| [Meta AI-assisted RCA](systems/meta-ai-rca.md) | Internal tool described in an engineering article | Narrowing change candidates, ranking, confidence filtering, incident-start evaluation | Full causal diagnosis across arbitrary failures or multi-agent orchestration |
| [Meta DrP](systems/meta-drp.md) | Deployed internal investigation platform; engineering article and paper | Structured context/findings, dependency DAGs, retries, timeouts, backtesting | A six-agent LLM system or token-based evaluation |
| [Microsoft RCACopilot](systems/microsoft-rcacopilot.md) | Implemented internal research system; paper | Diagnostic workflows and historical incident retrieval | Six-agent collaboration or classification scores equivalent to incident diagnosis accuracy |
| [Alibaba RCAgent](systems/alibaba-rcagent.md) | Industrial controller/expert system described in a paper | Evidence snapshots, expert tools, malformed-action feedback | A public runnable release or the assignment's full critic/reporting protocol |
| [mABC](systems/mabc-multi-agent-rca.md) | Seven-agent research prototype with public code | Explicit specialists, iterative scheduling, topology/fault representation | Paper voting and bounds fully enforced by the inspected code path |
| [IBM ITBench SRE agents](systems/ibm-itbench-sre-agent.md) | Archived CrewAI agent and a distinct replacement framework | Concrete tools, output schemas, evaluation infrastructure | Old sequential two-agent design satisfying this assignment; current tools inheriting old scores |

## Requirement-by-requirement evidence map

This table identifies where to read, not a certification that any single system satisfies the assignment in full.

| Assignment question | Useful references | Evidence boundary |
| --- | --- | --- |
| How do agents collaborate meaningfully? | Uber, incident.io, Resolve, mABC | Look for assignments, structured findings and feedback changing subsequent work, not just agent names |
| How does a critic change the result? | incident.io, Resolve | Their public accounts are strong role evidence; exact rejection schemas and stop policies remain unknown |
| How do we keep competing explanations? | Datadog, incident.io, Meta AI RCA | A ranked code change is narrower than a causal hypothesis; branch status is not calibrated probability |
| How do tools preserve evidence? | HolmesGPT, RCAgent, DrP | Call IDs, structured findings and snapshot keys are complementary patterns; raw-source access still matters |
| What does parallelism need? | Uber, DrP, HolmesGPT | Parallel agents, dependency-aware analyzer DAGs and parallel tool calls are different mechanisms |
| How can work recover and stop? | DrP, Uber, HolmesGPT | Published limits cover different layers; no reviewed example is a complete assignment specification |
| When should a result remain inconclusive? | Datadog, Meta's confidence filtering, evaluation note | Withholding a suggestion and a final insufficient-evidence report are distinct behaviors |
| How do we compare approaches fairly? | Datadog, AIOpsLab, ITBench, RCAEval, HolmesGPT | Reuse evaluation principles; do not compare headline numbers from unlike tasks |

Benchmark-specific details and sources are in [evaluation-landscape.md](evaluation-landscape.md). AIOpsLab and RCAEval are additional evaluation references, rather than additional claimed six-agent investigation systems.

## Patterns worth discussing, with their costs

| Pattern observed in research | Potential benefit | Cost / failure mode to test |
| --- | --- | --- |
| Scoped specialist questions | Less irrelevant context per investigator | Specialists can miss cross-service evidence outside their assigned scope |
| Deterministic collection plus adaptive investigation | Predictable execution around uncertain reasoning | A fixed collector can omit evidence needed for unusual incidents |
| Independent adversarial verification | Challenges self-confirming conclusions | More calls/latency; a weak verifier can repeat the same mistake |
| Shared evidence with source IDs and revisions | Auditable collaboration and report generation | Incorrect summaries can spread unless original evidence and revisions remain inspectable |
| Hypothesis-specific evidence retrieval | Tests causality instead of collecting every alarming signal | Narrow hypotheses can anchor the search and exclude alternatives |
| Explicit bounds at several layers | Prevents runaway calls and hanging investigations | Hard limits may end a valid investigation; the report must explain that limitation |
| Snapshot replay with hidden labels | Reproducible equal-input evaluation | Over-clean snapshots, leaked outcomes and narrow incident mixes inflate results |

These trade-offs are analytical deductions from the case studies, not independently measured comparative results.

## Numbers that should not be placed on one leaderboard

Uber's developer-fix agreement, Meta's top-five culprit retrieval, RCACopilot's category F1, RCAgent's semantic similarity and trajectory completion, ITBench's scenario resolution, and commercial vendors' latency claims measure different outcomes. A PR merge rate is neither RCA accuracy nor incident resolution rate. Exact scopes and limitations are retained in the individual notes.

The research does not show that adding agents automatically beats one agent. That is the central empirical question the assignment asks us to test with the same tools and a transparent accounting of cost and latency.
