# Alibaba RCAgent — controller, expert tools and evidence snapshots

Research checked: 2026-10-20. Type: industrial research system integrated into Alibaba Cloud's Flink diagnosis workflow; public runnable implementation not verified. Relevance: practical agent-tool reliability and evidence handling.

## What is already built

RCAgent uses a controller with code-analysis and log-analysis expert agents. The authors report integration into Alibaba Cloud's Real-time Compute Platform for Apache Flink. Their implementation uses locally hosted Vicuna-13B and GTE embeddings. [CIKM 2024 paper, abstract and sections 3–4](https://arxiv.org/html/2310.16340v3)

## Documented architecture

```text
Incident -> controller thought/action/observation loop
              |-> narrow data-query tools
              |-> code expert: recursive source inspection
              |-> log expert: partition, retrieve, analyze evidence
              |-> observation store: preview + snapshot key
           -> action validation / error feedback -> controller
           -> finalize / aggregate alternative continuations
```

JSON carries actions; snapshot keys retain full observations outside the prompt. Log evidence is checked against source chunks. Stabilization includes JSON regeneration, duplicate-call detection and premature-finalization feedback. Trajectory sampling begins near finalization to reuse earlier work. [Paper, section 3](https://arxiv.org/html/2310.16340v3)

## What the results mean

On 161 curated anomalous Flink jobs, root-cause METEOR is 15.15 versus ReAct's 6.44. Reported trajectory completion within 15 steps is 99.38%, versus 86.33%. Completion is not root-cause accuracy; semantic scores are not exact-match correctness. [Paper, Tables 1 and 4](https://arxiv.org/html/2310.16340v3)

## Assignment interpretation

The strongest investigation ideas here are a reference-preserving evidence store and explicit invalid-action feedback. Keeping large observations outside model context may help cost, but a preview must not hide decisive contradictory evidence. Evidence text matching can verify that a quotation exists; it cannot establish that the quotation proves a hypothesis.

| Assignment concern | Implication for later discussion |
| --- | --- |
| Orchestrator and observability collaboration | Controller/expert separation offers a useful comparison point. |
| Dependency specialist, critic, reporter | Our assignment must establish these responsibilities separately. |
| Bounded retry and termination | Distinguish formatting repair, tool retry and overall investigation limits. |
| Agent/tool failure recovery | A malformed action, timeout and missing record need different outcomes. |
| Competing explanations and confidence | Agreement between sampled answers cannot substitute for evidence quality. |
| Same-tools single-agent evaluation | Include every expert-agent model call when counting tokens and latency. |

## Availability and limits

This research verified a paper describing an implemented industrial system, not an officially supported open-source package. The private Flink setting and curated labels restrict direct reproducibility. No public code/data license was verified. Do not assume a similarly named GitHub “rca-agent” repository is this paper's artifact.

## Source ledger

- [Primary paper: RCAgent, arXiv 2310.16340 version 3](https://arxiv.org/html/2310.16340v3), dated 2024-08-02; CIKM 2024. Accessed 2026-10-20. Architecture, deployment and results are author reports; no deployment or benchmark was executed during this research.

[Back to research overview](../index.html)
