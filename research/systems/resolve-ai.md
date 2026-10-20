# Resolve AI — production investigation agents

Research date: 2026-10-20. Category: commercial production product. Relevance: **very high for parallel hypothesis investigators, an independent verifier, shared evidence, and comparison with a prior single-primary-agent architecture**.

## What is actually built

A named DoorDash Ads customer story reports deployment beginning in mid-2025, access to production code/infrastructure/telemetry after security review, and engagement by more than fifty engineers. It describes correlation across logs, metrics, traces, deployments, and dependencies. This is first-party vendor/customer evidence of use, not independent access to DoorDash's systems. [R1](https://website-prod.resolve.ai/customers/doordash)

The story's “up to 87%” improvement comes from a specific incident: the agent reportedly identified a cause in 15 minutes and the human reached the same finding roughly two hours later. It should not be converted into an average production result. [R1](https://website-prod.resolve.ai/customers/doordash)

## Public architecture and why it changed

The engineering retrospective identifies three current agent types: hypothesis investigators, adversarial verifiers, and stakeholder communicators. Investigators work in parallel with focused evidence; a shared evidence layer survives a session. The verifier checks the claim against evidence without having committed to the initial theory. [R2](https://resolve.ai/blog/Failures-That-Led-to-2x-Agent-Accuracy-Improvement)

```text
Incident / alert
  → investigation framed by a lead
  → parallel specialist hypothesis investigations
  → independent evidence verification
  → evidence-backed report and stakeholder communication
  ↔ shared production context and evidence
```

This is a combined simplification of two public explanations, not a documented internal queue topology. The separate harness article describes the lead, specialist routing, context selection, and verification. It says model routing considers cost and distinguishes reading systems from governed write actions. [R3](https://website-prod.resolve.ai/blog/6-pillars-of-agentic-harness-needed-for-investigations)

The retrospective attributes previous failures to saturated context, self-confirming reasoning, and poor reuse of learning. It reports **more than 2x root-cause quality** relative to its prior single-primary-agent architecture on an internal benchmark. That predecessor still used bounded helper agents. Dataset, exact scoring, absolute accuracy, and equal tool/budget controls are not public there. This is a **vendor claim**, not an independently controlled six-agents-versus-one result. [R2](https://resolve.ai/blog/Failures-That-Led-to-2x-Agent-Accuracy-Improvement)

## Concrete operating contracts

The documented REST API starts investigations asynchronously, returns `202 Accepted`, and exposes completion status plus versioned Markdown reports. It documents malformed-request, authentication, and missing-alert errors. Timing fields distinguish first hypothesis, converged RCA, and investigation completion; elapsed durations exclude waits for human replies. These are externally documented contracts, not proof of internal retry implementation. [R4](https://docs.resolve.ai/resolve-rest-api)

The limits page separates lightweight triage and deep investigation budgets. Defaults shown at access are 250 triages/hour and 750/day, versus 30 deep investigations/hour and 100/day; adaptive mode starts with triage and may escalate. It also documents pausing a channel subscription after 96 hours of inactivity and catching up after resumption. These are organization/product limits, **not per-incident token caps**. [R5](https://docs.resolve.ai/limits)

## Direct assignment mapping

| Requirement | Research assessment |
| --- | --- |
| Orchestrator | Public lead/coordination description is relevant; exact task graph undisclosed. |
| Observability and dependency agents | Focused specialists and relevant data are documented; exact assignment roles are not a published one-to-one match. |
| Reasoning, critic, reporter | Investigator, verifier, communicator are strong conceptual correspondences. |
| Genuine collaboration | Independent verification and shared evidence are stronger evidence than sequential differently prompted calls. |
| Ranked hypotheses / contradictory evidence / confidence | Verification is documented; exact rank ordering, contradiction schema, calibrated confidence, and final abstention contract remain unverified. |
| Limits and failure recovery | Product rate limits and API errors are concrete; retry counts, transient tool recovery, checkpointing, and cancellation semantics remain unknown. |
| Required evaluation | Vendor comparison is motivating; assignment still needs its own ten incidents, equal tools, and all five metrics. |

Later discussion questions, **our analysis**: What can the verifier reject? Can it demand new evidence rather than rewrite the report? Is shared evidence separate from an agent's private context? How does a budget apply to all concurrent branches? How are first useful evidence and final RCA measured separately? No architecture choice is made here.

## Source ledger

All sources are first-party; accessed **2026-10-20**. Undated live docs do not establish historical availability of every current field.

| ID | Source and direct link | Publication / update | Used for |
| --- | --- | --- | --- |
| R1 | [Powering Uninterrupted Ads for DoorDash Advertisers](https://website-prod.resolve.ai/customers/doordash) | Search-visible date 2026-01-16; separate update not shown | Deployment, integrations, scoped customer result |
| R2 | [The Failures That Led to 2x Agent Accuracy Improvement](https://resolve.ai/blog/Failures-That-Led-to-2x-Agent-Accuracy-Improvement) | Live body shows 2026-06-26; indexed rendering also shows 2026-07-17; date inconsistency retained | Agent types, shared evidence, prior architecture, internal comparison |
| R3 | [6 Pillars of an Agentic Harness needed to run and fix software](https://website-prod.resolve.ai/blog/6-pillars-of-agentic-harness-needed-for-investigations) | Live article 2026-07-01; separate update not shown | Lead, parallel specialists, model/context routing, governed actions |
| R4 | [Resolve REST API](https://docs.resolve.ai/resolve-rest-api) | Undated live documentation | Async lifecycle, errors, versioned reports, milestone timing |
| R5 | [Limits](https://docs.resolve.ai/limits) | Undated live documentation | Separate triage/deep rate limits; subscription pause/resume |

Evidence boundary: no proprietary implementation was inspected. Detailed production topology, internal message schemas, numerical confidence calibration, and retry/budget algorithms should not be invented from marketing language.
