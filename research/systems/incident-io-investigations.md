# incident.io — Investigations

Research date: 2026-10-20. Category: commercial production product. Relevance: **very high; one of the clearest published matches for the assignment's Critic Agent and evidence revision requirements**. Priority: read alongside Uber's system before deciding anything.

## What exists, and what problem it solves

The July 2025 launch states that Investigations was running in production internally and with a small group of customers. It connects telemetry, code changes, previous incidents, and chat context, returns cited findings in Slack or Microsoft Teams, and lets responders ask follow-ups. The launch's “up to 80%” MTTR reduction is an early **vendor claim**, with no controlled benchmark provided there. [I1](https://incident.io/blog/introducing-ai-sre)

Its value for this assignment is the engineering detail published later, rather than the launch's illustrative incident story. Do not treat that payment-service walkthrough as a reproducible test case.

## Publicly documented architecture

The October engineering account describes this simplified flow. [I2](https://incident.io/blog/building-investigations-what-it-takes-to-build-an-ai-sre)

```text
Incident
  → parallel checks of deployment / telemetry / chat and other sources
  → evidence-backed findings
  → hypothesis synthesis
  → adversarial agent attempts disproof
  → further investigation loop
```

Findings are persistent records with citations. New evidence can cancel an earlier finding; updates are written incrementally. This provides concrete evidence of state revision and disagreement changing the investigation. The source also describes retrospective testing with time-frozen inputs and warns against leaking the eventual fix or postmortem. [I2](https://incident.io/blog/building-investigations-what-it-takes-to-build-an-ai-sre)

The September changelog separately confirms a tree of checks, distinct finding/hypothesis/reviewer agents, and a later summary. Checks can be telemetry queries, code searches, or runbook-following work. [I3](https://incident.io/changelog/investigations-are-2x-faster)

## Important nuance: early evidence is not the reviewed final conclusion

A September optimization lets evidence-rich checks send useful updates before the full hypothesis/review sequence completes. A notification must contain concrete evidence, add something new, arrive before humans already handle the situation, and change the next action. The reviewed investigation continues. [I3](https://incident.io/changelog/investigations-are-2x-faster)

This distinction matters when reading vendor latency. The changelog reports median time to an accurate channel update dropping from **6.7 to 3 minutes**, with updates within five minutes rising from **8% to 68%**. This is a vendor-reported communication metric, not a measured reduction in final root-cause latency or proof that review is unnecessary. [I3](https://incident.io/changelog/investigations-are-2x-faster)

## Data, reliability, and evaluation boundaries

The published design is stronger evidence for mutable findings and adversarial review than for low-level infrastructure. It does not publish a complete structured exchange schema, retry policy, timeout handling, or failure-recovery implementation. The exact five-tool assignment contract and six named roles cannot be inferred.

The engineering article's backtesting grades hypotheses against historical response outcomes. It is not a public experiment comparing six agents against an equal-tools single-agent baseline with accuracy, grounding, calls, latency, and tokens. [I2](https://incident.io/blog/building-investigations-what-it-takes-to-build-an-ai-sre)

## Direct assignment mapping

| Requirement | What this research establishes / leaves open |
| --- | --- |
| Parallelism | Explicit parallel source checks. |
| Critic collaboration | Explicit adversarial disproof followed by another investigation loop. |
| Shared state | Evidence-backed findings may be revised and canceled. |
| Contradictory evidence | An old finding need not remain accepted after new observations. |
| Reports and confidence | Cited channel findings exist; the exact ranked-hypothesis output schema and numeric confidence calibration are unverified. |
| Simulated failures, retries, budgets | No complete policy established by the selected sources. |
| Evaluation | Historical replay is relevant; all assignment experiments remain our responsibility. |

Questions for the later design discussion, **our analysis**: Can the critic name a missing observation and cause a specific tool call? Can a record retain its history when superseded? Does an early update have a different status from a final conclusion? Can evaluation replay the same incident without any evidence created after the incident start? These questions help turn attractive agent diagrams into observable behavior without committing to a framework.

## Source ledger

All sources are first-party and were accessed **2026-10-20**. Separate modification dates were not shown.

| ID | Source and direct link | Published | Used for |
| --- | --- | --- | --- |
| I1 | [Investigations has entered the chat](https://incident.io/blog/introducing-ai-sre) | 2025-07-02 | Explicit production deployment, product scope, early vendor outcome claim |
| I2 | [Building Investigations: what it takes to build an AI SRE](https://incident.io/blog/building-investigations-what-it-takes-to-build-an-ai-sre) | 2026-10-01 | Parallelism, adversarial critic, evidence record revision, time-frozen evaluation |
| I3 | [Investigations are 2x faster](https://incident.io/changelog/investigations-are-2x-faster) | 2026-09-22 | Separate agent roles, early notifications, operational latency definition |

Evidence boundary: the architecture is a simplified reading of public engineering descriptions. We did not inspect proprietary code, reproduce reported results, or establish undocumented tool-failure handling.
