# Agent-contract research and reanalysis

Rechecked primary sources on 20 October 2026. This note records the reasoning behind the separate [agent contracts](agents/README.md), not new production results or a claim that another system uses our exact seven roles. D2 remains removed; D1 owns reasoning plus orchestration.

## Research findings and design decisions

| Primary source | What the source establishes | Our design decision / limit |
| --- | --- | --- |
| [Anthropic multi-agent Research](https://www.anthropic.com/engineering/multi-agent-research-system) | Delegation needs objectives, output expectations, source/tool guidance and task boundaries; asynchronous work introduces state-consistency difficulties. | Stable expertise, dynamic bounded assignments, explicit D1 bootstrap and versioned results. Research-agent results do not establish incident-diagnosis accuracy. |
| [Resolve engineering retrospective](https://resolve.ai/blog/Failures-That-Led-to-2x-Agent-Accuracy-Improvement) | Focused investigators, shared evidence and structurally independent verification address failures in its earlier designs. | D7 sees originals and can demand rival checks. We do not restore D2 or claim that a separate context guarantees independence. Vendor benchmark gains are not our results. |
| [incident.io engineering account](https://incident.io/blog/building-investigations-what-it-takes-to-build-an-ai-sre) | Cited findings can be cancelled by later evidence; evaluation freezes incident inputs to avoid future-answer leakage. | Invalidate dependent interpretations and stale approvals; evaluate time-appropriate evidence. Exact approval hashes and delivery guards are our proposal. |
| [OpenTelemetry messaging conventions](https://opentelemetry.io/docs/specs/semconv/messaging/messaging-spans/) | Producer/consumer relationships can require message context and span links. The page is marked Development. | D3 correlates asynchronous evidence without requiring one trace ID; missing spans remain coverage gaps. Pin adapter/instrumentation versions; do not impose one universal event schema. |
| [Sourcegraph precise navigation](https://sourcegraph.com/docs/code-navigation/precise-code-navigation) | Repository/language-specific indexes support code navigation, with search fallback. | D4 discovers relevant versioned behavior without scanning every repository. Static references do not prove dynamic routing or business intent. |
| [SLSA provenance](https://slsa.dev/spec/v1.1/provenance) | Build provenance describes artifacts and build inputs. | D4 binds deployed artifacts to source when actual records permit it. This is not automatically a complete runtime configuration map. |
| [PostgreSQL transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html) | Different query/transaction snapshots can observe different states; concurrency requires explicit consistency handling. | D5 records query snapshot versus incident-time history; our case store uses version-checked application rules. No database technology or long-running production transaction is prescribed. |
| [Langfuse tracing](https://langfuse.com/docs/observability/overview), [prompt links](https://langfuse.com/docs/prompt-management/features/link-to-traces) | Traces expose generation/tool/retrieval inputs and outputs; generations can link to managed prompt versions. | D6 inspects actual run artifacts. A prompt/version link alone does not prove why a model responded incorrectly. |
| [Twilio outbound statuses](https://www.twilio.com/docs/messaging/guides/track-outbound-message-status) | Outbound message lifecycle/status callbacks distinguish sending and delivery outcomes. | D3 and D8 separate provider acceptance, delivered status and customer visibility; status meaning is channel-specific. |
| [OWASP prompt injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) | External content can inject instructions; mitigation needs constrained capabilities and trust boundaries. | Source content is evidence, not authority. Validate tools/permissions outside all agents, including reviewer/writer; do not claim perfect prevention. |

## What changed after reanalysis

1. Made D1's initial navigation/source access explicit: it is not blind, but does not have a hidden correct workflow.
2. Defined one shared Task/Result protocol instead of seven incompatible envelopes. Per-agent documents specify extensions and actual examples.
3. Added applicability checks for late parallel results; a global revision change alone is not sufficient to reject useful independent evidence.
4. Bound final approval to exact report and dependency versions; material changes revoke affected approval, not automatically every approval on any case event.
5. Defined deterministic `investigation_incomplete` delivery when valid final review is unavailable. This is distinct from a reviewed inconclusive diagnosis.
6. Preserved code/data/AI discovery before implementation-specific questions, original-source review and explicit unknowns.
7. Made the investigator's own failure modes testable: false premises, stale scope, summary drift, duplicate results, review outages and unsupported confidence.

## Remaining implementation decisions

Choose actual adapters, authorization implementation, case-store transaction/version strategy, model/provider, prompt versions, typed schemas and numerical budgets through implementation/testing. Decide material-change heuristics and measure false-positive/false-negative review invalidation. Evaluate review granularity and caching under high-fanout incidents; do not claim free or perfect review. Add human evaluation for intended-behavior ambiguity and rare causal errors.

No agent or pipeline has been implemented, run against live systems or load-tested here. The documents are ready for contract-level discussion and implementation planning; tests in them are planned acceptance criteria.
