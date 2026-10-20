# Meta — AI-assisted root-cause isolation

Research date: **2026-10-20**. Relevance: **high for ranked hypotheses, candidate narrowing, uncertainty, and evaluation**; limited evidence of multi-agent coordination. Status: an internal investigation tool described by Meta in 2024, not a public runnable product.

## Established system

Meta's system finds code changes that may explain an incident. Heuristics narrow thousands of changes to hundreds using ownership and runtime-code relationships. A fine-tuned Llama 2 7B ranker repeatedly evaluates groups of at most 20 changes, retains five per group, and aggregates successive elections until five candidates remain. Historical incidents supply training/evaluation labels. Meta reports the true cause appears in the top five for **42% of backtested web-monorepo investigations**, using information available when the investigation began. It also describes suppressing low-confidence suggestions and prioritizing reproducibility and employee feedback. [Official source, June 24, 2024](https://engineering.fb.com/2024/06/24/data-infrastructure/leveraging-ai-for-efficient-incident-response/).

```text
Incident-start context + candidate code changes
                    |
   heuristic retrieval: thousands -> hundreds
                    |
 LLM elections: <=20 changes -> best 5 per group
                    |
       aggregate -> repeat -> final top 5
                    |
 confidence filtering + explainable responder view
```

This flow reconstructs the official description. Repeated ranker calls are **not evidence of distinct collaborating agents**. No critic agent, failure-recovery protocol, or tool retry budget is established by this publication. [Official source](https://engineering.fb.com/2024/06/24/data-infrastructure/leveraging-ai-for-efficient-incident-response/).

## How to read the result

The 42% number is **top-five culprit retrieval**, not top-one diagnostic accuracy, not 42% of arbitrary infrastructure incidents, and not a multi-agent-versus-single-agent win. The candidate space is code changes; environmental failures without a culprit change need a wider formulation. The reviewed source does not establish a controlled equal-tools agent baseline.

## Assignment connection and questions to retain

| Requirement | Research implication / limitation |
|---|---|
| Dependency investigation | Candidate narrowing is relevant when many deployments precede an alert. A later prototype must still inspect service dependencies and configuration evidence. |
| Ranked competing hypotheses | A final ranked list is useful; code-change candidates are narrower than causal explanations. We still need supporting **and contradicting** evidence per hypothesis. |
| Confidence / inconclusive outcome | A precision-versus-coverage policy is worth evaluating. We must define how confidence is computed and what “insufficient evidence” means. |
| Critic and feedback | A critic could test whether a candidate survived only because the true cause was excluded upstream. This is our analysis, not a published Meta agent role. |
| Evaluation | Incident-start evidence helps avoid leaking later remediation into the diagnosis. Report top-one and top-k separately if both are measured. |

## Borrowable lessons, without choosing a design

The main lesson is to evaluate retrieval separately from reasoning: a ranker cannot recover a cause that was removed before ranking. A synthetic dataset can expose this with a temporally nearby but irrelevant deployment and a dependency failure outside the obvious owning service. These are suggested evaluation ideas, not Meta's published test cases.

Do not infer calibration, explicit contradiction handling, distributed state, parallel specialists, robust incomplete-tool semantics, or agent recovery from the article. Those remain separate assignment requirements.

## Source ledger

- **Primary:** [Leveraging AI for efficient incident response — Engineering at Meta](https://engineering.fb.com/2024/06/24/data-infrastructure/leveraging-ai-for-efficient-incident-response/), published **2024-06-24**, accessed **2026-10-20**. All established system claims above come from this source; proposed assignment implications are analysis.
