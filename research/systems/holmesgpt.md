# HolmesGPT: inspectable investigation loop and tooling reference

Research date: 20 October 2026. Category: implemented open-source SRE agent. Relevance: high for tools, reliability details, and baseline design; incomplete evidence for the assignment's six-agent collaboration requirement.

## What already exists

HolmesGPT is a working open-source production troubleshooting agent, originally created by Robusta. Its public repository provides CLI/server code and an Apache-2.0 license. It investigates by calling tools against connected infrastructure and observability services. The project lists Kubernetes, Prometheus, Datadog, Loki, Tempo, deployment tools, and incident/documentation integrations. This is substantially more useful as an implementation reference than a conceptual agent diagram. [Repository and README](https://github.com/HolmesGPT/holmesgpt)

The reviewed code snapshot is commit `b92fdd9dd8fcd41e8cf79ac367802f018bfe9cb2`, committed 19 October 2026. Code links below are pinned to that snapshot, while public documentation pages are versioned separately. Features from separate versions should be checked together before reuse. [Pinned repository](https://github.com/HolmesGPT/holmesgpt/tree/b92fdd9dd8fcd41e8cf79ac367802f018bfe9cb2)

## Architecture and investigation flow

This is a simplified reading of the public code and runbook documentation, not a vendor-supplied deployment diagram.

```text
Question or alert + configured toolsets
                 |
        Initial investigation context
                 |
          LLM chooses tool calls <-------------------+
                 |                                 |
      Tool executor runs requested queries          |
                 |                                 |
    Structured results / explicit errors            |
                 |                                 |
     Update conversation + usage statistics --------+
                 |
      Final answer, cancellation, or step limit

Optional: match a runbook catalog entry -> fetch relevant runbook
          -> gather evidence for its troubleshooting steps
```

Runbooks are matched from catalog descriptions and fetched on demand. They work through the CLI, server, and SDK, and findings can show completed or skipped steps. This is an example of retrieving focused procedural knowledge rather than injecting every runbook into the initial prompt. [Runbooks documentation, v0.23.0](https://holmesgpt.dev/0.23.0/reference/runbooks/)

## Inspectable implementation details

The pinned tool-calling implementation uses an iterative loop, compacts context when needed, and executes a batch of tool calls through a thread pool with up to 16 workers. Tool lookup and invocation failures become explicit error results. Cancellation is checked, and model iterations are bounded by `max_steps`; exhaustion can raise an exception, so graceful inconclusive reporting is a separate concern. These are code observations, not measured reliability guarantees. [Tool-calling implementation](https://github.com/HolmesGPT/holmesgpt/blob/b92fdd9dd8fcd41e8cf79ac367802f018bfe9cb2/holmes/core/tool_calling_llm.py)

`ToolCallResult` carries a call ID, tool name, description, structured result, and optional size and toolset name. Formatting includes tool metadata and original parameters, making it possible to trace a claim back to a specific query. This is a concrete provenance pattern to inspect. [Result models](https://github.com/HolmesGPT/holmesgpt/blob/b92fdd9dd8fcd41e8cf79ac367802f018bfe9cb2/holmes/core/models.py)

The reviewed configuration defaults `max_steps` to 100. That is this project's setting, not a recommended assignment budget. [Configuration source](https://github.com/HolmesGPT/holmesgpt/blob/b92fdd9dd8fcd41e8cf79ac367802f018bfe9cb2/holmes/config.py)

## Data and assignment tool coverage

| Assignment source | Relevant integration or pattern | Qualification |
| --- | --- | --- |
| Logs | Kubernetes logs, Loki, Datadog | Query scope and available history depend on setup |
| Metrics | Prometheus, Grafana, Datadog | Requires credentials and meaningful labels |
| Deployments/config | ArgoCD, Helm, resource state and change integrations | Integration availability is not proof that every investigation queries changes |
| Service dependencies | Traces, Kubernetes objects, connected documentation | A complete historical dependency graph is not established here |
| Historical incidents | Incident and knowledge-system integrations | Retrieval and access differ by connector |

The integration inventory supports these as available data paths, not mandatory stages. [Integration inventory](https://github.com/HolmesGPT/holmesgpt#-data-sources)

## Multi-agent distinction

The investigated core is an agentic tool loop. Parallel queries are visible in code. Those facts do not by themselves establish distinct orchestrator, observability, dependency, reasoning, critic, and reporting agents exchanging structured findings. A faithful reuse for the assignment would need additional coordination evidence or additional implementation. This makes HolmesGPT particularly useful as a reference for a capable single-agent baseline; that is our interpretation, not a published comparison result.

## Evaluation practices

The versioned evaluation guide describes more than 150 evaluations, difficulty categories, regression tests, repeated runs, and model comparisons. It also documents expected-output fixtures and optional Braintrust analysis. These practices are relevant to building a reproducible assignment evaluation. The guide describes scheduling in more than one way, so inspect CI configuration before assuming a particular cadence. No headline model accuracy is imported here: counts and success rates depend on the selected suite, model, judge, and snapshot. [Evaluation guide, v0.21.0](https://holmesgpt.dev/0.21.0/development/evaluations/)

## What is worth considering later

- Explicit error-bearing result objects and persistent tool-call identifiers.
- Iterative targeted queries rather than a single telemetry summary.
- Context limits and cancellation alongside an iteration budget.
- On-demand runbook loading.
- Regression scenarios and repeated measurements.

## Gaps relative to the assignment

This note does not establish an independent critic, mandatory ranked competing hypotheses, a structured counterevidence ledger, calibrated confidence, or an explicit inconclusive outcome. Thread-pool execution does not establish safe dependency scheduling for every tool. A step bound does not prove bounded retries for every connector or a global wall-clock deadline. Its external-data integrations are useful examples, but the assignment specifically permits simulated data; recreating a live Kubernetes deployment is unnecessary merely to learn these patterns.

## Sources and freshness

All sources were accessed on 20 October 2026. Repository snapshot date: 19 October 2026. Documentation publication dates are not clearly stated; version paths are recorded above. Code was inspected read-only; the project was not installed, run, or benchmarked in this research.

- [Project repository, license, and integration inventory](https://github.com/HolmesGPT/holmesgpt)
- [Pinned code snapshot](https://github.com/HolmesGPT/holmesgpt/tree/b92fdd9dd8fcd41e8cf79ac367802f018bfe9cb2)
- [Tool-calling loop](https://github.com/HolmesGPT/holmesgpt/blob/b92fdd9dd8fcd41e8cf79ac367802f018bfe9cb2/holmes/core/tool_calling_llm.py)
- [Structured result models](https://github.com/HolmesGPT/holmesgpt/blob/b92fdd9dd8fcd41e8cf79ac367802f018bfe9cb2/holmes/core/models.py)
- [Configuration](https://github.com/HolmesGPT/holmesgpt/blob/b92fdd9dd8fcd41e8cf79ac367802f018bfe9cb2/holmes/config.py)
- [Runbook documentation, v0.23.0](https://holmesgpt.dev/0.23.0/reference/runbooks/)
- [Evaluation documentation, v0.21.0](https://holmesgpt.dev/0.21.0/development/evaluations/)
