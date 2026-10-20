# Assignment: what the research needs to answer

Source: [Orange Invest Assignment FE (1).pdf](../Orange%20Invest%20Assignment%20FE%20%281%29.pdf), both pages, read in full. Research date: 20 October 2026.

## Objective and scope

Build a multi-agent system that investigates production incidents, proposes probable root causes, and recommends corrective actions grounded in evidence. It receives an incident report and has access to simulated logs, performance metrics, deployment history, service dependencies, and historical incident reports. Access means these records are available through tools; the PDF does not say that relevant records are already selected or injected into the first prompt. Inputs can be incomplete, contradictory, or misleading. Investigation must involve seeking and testing evidence rather than generating a plausible explanation from the initial report.

This folder is the research phase requested by the user. The implementation, final architecture, framework choice, and final submission are future work. Flow diagrams in system notes describe existing systems, or are explicitly labeled interpretations.

The PDF is the minimum specification, not the complete product scope agreed in discussion. [Our current requirements](system-requirements.md) also require searchable codebase, database contents and diagnostics, deployment/infrastructure investigation, effective config/env, and AI application investigation: prompts, model settings, retrieval, tools, handoffs, shared state and coordination. Input can be vague free text without supplied evidence; discovery must establish the issue before causal diagnosis. These are user-established scope decisions, not claims about wording in the PDF.

## A. Agents and collaboration

The PDF says at least five distinct agents but explicitly lists six roles, without labeling them examples. That count is inconsistent; the role wording should not be silently treated as optional. The PDF does not prescribe a graph, framework, exact topology, or one agent per data source. We can choose our own architecture and add or specialize investigators while making the coverage of all six responsibilities explicit. The HTML distinguishes this requirement reading from its proposed design.

| Named role | Required responsibility | What to investigate in existing systems |
| --- | --- | --- |
| Orchestrator | Plan and coordinate the investigation | Task routing, dependencies, parallel work, stopping decisions |
| Observability Agent | Investigate logs and metrics | Targeted queries, signal extraction, time windows, missing telemetry |
| Dependency Agent | Examine deployments, config changes, and dependencies | Change correlation, causal chains, service topology |
| Reasoning Agent | Develop and compare competing hypotheses | Alternatives, hypothesis revisions, falsification |
| Critic Agent | Challenge conclusions and request more investigation when evidence is weak | Independent verification, contradictions, feedback to investigators |
| Reporting Agent | Produce the final investigation and remediation report | Provenance, uncertainty, actionable recommendations |

Agents must exchange structured results and collaborate. A sequence of differently prompted LLM calls is expressly insufficient. A product being marketed as an AI SRE does not establish that it has this collaboration model.

## B. Tools

Five data capabilities are required: querying logs, querying metrics, querying deployment history, querying service dependencies, and querying historical incidents. Each tool needs structured inputs and outputs, error handling, and simulated failures, including timeouts or incomplete results.

Research should distinguish an empty successful query from an unavailable source. Absence of observed errors is not evidence of a healthy service when a query timed out. This distinction is an analytical implication of the failure requirements.

## C. Orchestration and reliability

- Execute independent tasks in parallel.
- Maintain shared investigation state and task dependencies.
- Gather additional evidence through feedback loops.
- Bound retries and execution, and define termination conditions.
- Recover from failures of agents or tools.

Evidence of parallel tool execution alone does not prove independent collaborating agents. A published workflow diagram alone does not prove durable state, retry policies, or partial-result recovery; these need separate evidence.

## D. Evidence and conclusions

Final reports must contain ranked hypotheses, supporting evidence, contradicting evidence, confidence levels, and recommended actions. Facts must be distinguished from assumptions. An inconclusive result must be possible when evidence does not justify a conclusion.

Confidence scores reported by products are not automatically calibrated probabilities. A source that merely promises an accurate RCA does not establish contradiction handling or abstention.

## E. Evaluation

Create at least ten test incidents covering misleading clues, conflicting observations, and tool failures. Compare the multi-agent implementation with a single-agent baseline using the same tools. Measure all five requested dimensions:

| Metric | Practical interpretation for later discussion |
| --- | --- |
| Root-cause accuracy | Correctness against hidden incident ground truth; define component, mechanism, and acceptable alternatives |
| Evidence grounding | Whether material claims have supporting evidence and handle counterevidence |
| Tool-call count | Include retries and failed calls; count all collaborating agents |
| Latency | End-to-end elapsed time; parallel branch times are not simply added |
| Token consumption | Sum model usage over every agent, retry, and report stage |

For a fair later experiment, holding the model and dataset constant in addition to tools would help isolate the effect of coordination. That is a methodological recommendation; only identical tools are explicit in the PDF. Ten incidents are a minimum demonstration, not enough to establish broad production reliability.

## F. Deliverables and constraints

1. Runnable implementation and setup instructions.
2. Architecture diagram and explanation of agent coordination.
3. Synthetic incident dataset and automated tests.
4. Results comparing multi-agent and single-agent approaches.
5. Technical note of at most 500 words covering decisions, trade-offs, limitations, and improvements.

Any language, LLM provider, or framework is allowed. AI coding assistants are permitted, and the assistant transcript must be included in the submission. Individual test-case answers must not be hardcoded. A polished frontend is not required. Incomplete functionality and external dependencies must be documented.

The HTML in this folder is a research reading aid, not an assignment requirement or an implementation frontend. This research session is not claimed to be a complete export of the coding-assistant transcript.
