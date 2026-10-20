# Microsoft RCACopilot — diagnostic workflows plus incident retrieval

Research checked: 2026-10-20. Type: implemented industrial research system; internal implementation. Relevance: evidence collection and historical incident retrieval, rather than the assignment's complete multi-agent design.

## What is already built

The EuroSys 2024 paper studies Microsoft email Transport incidents. It reports that the diagnostic collection component had operated at Microsoft for more than four years. That statement should not be expanded into four years of autonomous LLM diagnosis. No official runnable code or incident dataset was verified in this research. [Paper, abstract and implementation](https://arxiv.org/html/2305.15778v2)

## Documented architecture

```text
Incident / alert type
  -> engineer-authored diagnostic handler
  -> scope-switch / query / mitigation action nodes
  -> multi-source diagnostics
  -> short LLM summary
  -> retrieve similar historical incidents, weighted by recency
  -> LLM root-cause category and explanation
  -> engineer review
```

Handlers are reusable, versioned workflows. Retrieval uses FastText and selects five historical examples. Sources can include logs, stack traces and socket metrics. The published evaluation reports micro-F1 0.766 and macro-F1 0.533 for category prediction, with 4.205-second average inference in its experimental setting. These are classification measurements, not end-to-end investigation success or production MTTR. [Paper, sections 4–5 and Table 2](https://arxiv.org/html/2305.15778v2)

## Assignment interpretation

The transferable question is how to curate useful evidence and reuse historical cases. An analogous assignment experiment could check whether concise evidence improves diagnosis while retaining pointers to original records. This is an investigation idea, not an architecture decision.

| Assignment concern | Assessment for this reference |
| --- | --- |
| Six named specialist roles and critic | Do not count this reference as evidence that those roles are implemented. |
| Five simulated tool families | A handler pattern is relevant; the assignment still needs its own structured interfaces and failure cases. |
| Shared state, parallel tasks, recovery | Require separate implementation evidence and tests in our eventual solution. |
| Competing hypotheses and contradictions | A retrieved category is not enough to satisfy the required report. |
| Inconclusive outcome | Distinguish an unseen category from insufficient evidence. They answer different questions. |
| Fair single-agent baseline | Do not reuse this paper's scores as an expected result for our assignment. |

## Availability and limits

Treat this as a published reference whose architecture can be studied, not an installable starting repository. Public search did not establish a reusable implementation/data license; the paper's publication license does not license Microsoft's internal system. Avoid confusing this Microsoft project with the unrelated 2025 paper titled “RCA Copilot: Transforming Network Data into Actionable Insights.”

## Source ledger

- [Primary paper: arXiv 2305.15778, version 2](https://arxiv.org/html/2305.15778v2), EuroSys 2024 research; accessed 2026-10-20. The title evolved from “Automatic Root Cause Analysis…” to “Empowering Practical Root Cause Analysis…”. Deployment and performance statements above are author reports, not independently reproduced results.

[Back to research overview](../index.html)
