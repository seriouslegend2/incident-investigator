# Uber — Debug Assist

Research date: **2026-10-20**. Relevance: **very high**, especially the investigation harness, parallel specialists, shared state, and bounded execution. Status: **internal production system, according to its Uber engineer presenter**. This is the debugging system, not Uber's accessible-rides product called Uber Assist. No public runnable Debug Assist repository was established in this research.

## Read this first

Debug Assist investigates application-quality problems from existing Uber telemetry and can continue into mitigation, code repair, testing, and PR creation. It is a useful production precedent for the assignment's investigation engine. Its reported repair capabilities go beyond the assignment, which asks for evidence-backed recommendations and a fair evaluation; they should not silently expand our scope.

The strongest detailed evidence available here is **the user's complete local talk transcript and two slides**. Those have been read/viewed directly. Online research identifies the speaker as Kriti Dangi and corroborates her Debug Assist talk, but the original YouTube transcript could not be fetched independently because YouTube throttled access. Consequently, detailed implementation claims below are explicitly attributed to the supplied presentation, not independently audited production behavior.

## Evidence and source provenance

| ID | Source | Date and what it establishes |
|---|---|---|
| U1 | [Local complete talk transcript](../../uberassist/uberassist_youtube_transcript.txt) | No embedded publication date; ~29-minute presentation. Primary speaker account supplied by the user. Timestamp references below refer to this file. |
| U2 | [Local pipeline slide](../../uberassist/uberassist.png) | Slide 11; no date visible. Exact node names, model families, turn ceilings, structured XML, and runtime skill loading. |
| U3 | [Local productionization slide](../../uberassist/uberassist1.png) | Slide 12; no date visible. Eight agent types, five monorepos, shared Python code, PEX, Docker images, pipeline configs. |
| U4 | [Kriti Dangi's speaker profile and own talk announcement](https://in.linkedin.com/in/kriti-dangi-678743128) | Announcement for September 11 at AGNTCon + MCPCon Japan 2026, 11:30 JST, Tokyo. First-party speaker statement corroborates ~9,000 production issues/month and 11 MCP servers. Profile dynamically aggregates posts. |
| U5 | [Talk recording: How Uber's AI Agent Debugs Production Issues](https://www.youtube.com/watch?v=CacTDGs-If4) | Located through a secondary article. YouTube fetch was throttled, so upload date and independent transcript were not verified. Treat as a navigation link, with U1–U3 carrying the detailed evidence. |
| U6 | [Uber Engineering: Real-Time Analytics for Mobile App Crashes using Apache Pinot](https://www.uber.com/us/en/blog/real-time-analytics-for-mobile-app-crashes/) | November 2, 2023. Official corroboration for Healthline and its crash/exception analytics foundation, not a Debug Assist architecture publication. |

All online sources accessed 2026-10-20. [This October 6, 2026 secondary article](https://aayushostwal2.substack.com/p/9000-production-issues-a-month-how) was used only to locate the recording; its interpretations are not independent corroboration. A [translated reupload](https://www.youtube.com/watch?v=6YuIp-MwPv4) was also located, but is not the primary source for the technical claims.

## Problem and inputs

**Presentation account, U1 00:47–05:08:** Wisdom captures employee/beta-tester reports, such as a blank screen or battery issue, with app and OS version, city, screenshots, network logs, analytics, console output, GraphQL logs, and UI state. Healthline detects crashes, hangs, jitter, and other performance deterioration automatically, retaining session context and stack traces/crash dumps. These are already rich, joined evidence sources before the agent begins.

**Official independent background, U6:** Healthline is an internal crash/exception monitoring and analysis service for mobile applications and backend services. It groups similar failures into issues and helps identify change candidates and owners. The 2023 article describes Apache Pinot analytics, flattened metadata, separately stored compressed crash records, and sampling of raw records while retaining aggregation fields for all crashes. This explains why a production agent can ask narrow questions instead of ingesting every raw event. U6 does not demonstrate the later agent's exact query interface or data coverage.

Additional investigation inputs in U1 include distributed traces through Jaeger, logs, current incident records, code and Git history, feature flags, good/bad release versions, and module boundaries. A complete schema for metrics, historical-incident retrieval, dependency graphs, and deployment-history tools is not published in the supplied materials.

## Architecture as described, not a proposed assignment design

```text
Wisdom reports / Healthline automatic issue detection
                     |
           automatic severity + ownership triage
                     |
       deterministic context_collector
       fetch known APIs; parse/prune large logs
                     |
               classify / RCA
       category + requires_code_fix + confidence
       extra evidence via MCP when needed
                     |
          +----------+----------+
          |          |          |
    breadcrumbs   release    offending-commit
     / timeline  correlation    analysis
          |          |          |
          +----- consolidate ---+
                     |
                  fix node
       feature-flag correlation / mitigation;
       code search and candidate repair
                     |
                bazel_test
          reproduce and validate; bounded loop
                     |
                create_diff
     PR + issue links + metadata + engineer handoff
                     |
       engineer corrections / incremental edits
       / chat / prepared local or remote environment
```

This is a reconstruction from U1–U3. Three named RCA specialists are examples; the supplied talk does not enumerate all agents or establish that every example runs for every issue. The outer pipeline is intentionally fixed; LLM decisions and tool use occur inside its stages. The repair/testing loop is a separate concern from the initial parallel RCA fan-out.

## Components and concrete controls

| Component | Evidence from the supplied presentation | Why it matters |
|---|---|---|
| Workflow controller | LangGraph combines deterministic and LLM nodes. The platform supplies the stage sequence instead of asking the model to invent it. U1 09:07–09:50. | Coordination has explicit boundaries. This alone is not proof of multi-agent collaboration; the fan-out below supplies that evidence. |
| Context collector | Ordinary code fetches known sources and prunes very large logs. U1 09:50–10:41. | Data collection, context size, latency, and model spend are controlled before reasoning. |
| Classifier/RCA | Categories include application code, third-party library, infrastructure, and network. Outputs confidence and can request more evidence. U1 10:44–11:37; U2 shows XML and `category`, `requires_code_fix`, `confidence`. | Gives downstream stages machine-readable results, with a declared uncertainty field. Confidence calibration is not explained. |
| Parallel specialists | Breadcrumb reconstruction, crash-release correlation, and offending-commit analysis. Results are consolidated. U1 11:37–12:19 and 27:09–27:50. | Actual specialization and parallel evidence collection are explicitly described. The aggregator protocol and disagreement handling are unknown. |
| Shared state | State from earlier nodes is passed to later nodes. U1 13:16–13:26. | Supports continuity across stages; exact persistence/checkpoint/concurrency semantics are not specified. |
| Model/turn budgets | U2: Sonnet with 20 maximum turns for RCA; Opus with 30–50 for repair; Sonnet with 20 for testing and diff creation. | Per-task ceilings reduce runaway work. Exact model versions, dollar limits, wall-clock limits, and aggregate fan-out budgets are not given. |
| Pruned specialist scope | Offending-commit agent receives good/bad versions and a narrowed module, then searches the relevant interval. U1 27:09–27:50. | Limits irrelevant exploration and makes the task testable. |
| Validation | Unit tests first, then integration/component tests, then mobile simulator/emulator when needed. Retry count is fixed but unpublished. U1 14:20–14:53 and 22:45–24:48. | The system attempts reproducible validation, rather than equating plausible text with proof. It does not establish that every proposed fix passes. |
| Execution observability | Tracing covers LangChain/model calls, subagents, MCP calls, and Bash commands. U1 26:11–26:43. | A final report can be audited against execution. The transcript renders the tracing vendor as “arise”; the exact product spelling is not verified. |
| Human feedback | Diff-fixer, RCA chat and corrections, and prepared debugging environments. U1 17:51–19:22. | Engineer feedback improves prompts/skills; no formal online learning algorithm is specified. |

The presenter says investigations beyond roughly 20 turns often drifted in their experiments (12:31–12:59). This is an observed setting for their workload, not a universal optimal limit.

The mitigation stage can correlate a crash to a feature flag and roll it back when correlation is strong (13:28–14:17). The talk does **not** provide a complete authorization policy, threshold specification, approval mechanism, or rollback safety analysis. For this assignment, it is evidence that mitigation and permanent repair are separate concerns; it is not a requirement to perform production mutations.

## Scaling arrangement

U2–U3 and U1 15:14–17:47 describe a common harness with domain logic in skills/plugins loaded at runtime. Agent type selects the relevant specialization; the agent does not ingest the entire marketplace. Each agent type has its own Docker image, pipeline configuration, and marketplace plugin while sharing the Python implementation. Code is built with Bazel into PEX artifacts held in an artifact repository; jobs retrieve the executable and runtime dependencies.

At presentation time, the speaker reports about eight agent types across five monorepos and about 30 unique RCA subagents. **Eight agent types is not eight concurrent investigators per incident**, and 30 available specialists does not mean 30 are always executed. A projection of roughly 10,000 future specialists is an aspiration mentioned in Q&A, not an achieved deployment figure.

## Reported results and what they do not prove

All numbers below are **presenter-reported**, U1; not controlled results reproduced here.

| Reported quantity | Correct interpretation | Caution |
|---|---|---|
| ~9,000 deep RCAs/month | Monthly investigation volume, 19:27–19:39. | Not 9,000 autonomously resolved incidents. |
| 50% RCA accuracy | Exact agreement with developer fixes, 19:39–19:46. | Sample size, label rubric, incident mix, and denominator details are unpublished. |
| ~40% of the remaining half directionally useful | Roughly 20% of all cases under that reading; correct module/file may still miss the function. | Do not sum 50% + 40% to claim 90% accuracy. Even an approximate 70% exact-or-directional figure would mix two quality categories. |
| PR merge rate from 5% to ~48% over a year | Share of generated PRs merged, 20:21–20:37. | Not the fraction of all incoming reports fixed, and not proof all merged changes required no edits. |
| RCA in under 30 minutes | Pipeline capability statement, 05:41–05:47. | No p50/p95 latency, token/call count, or distribution supplied. |
| Battery issue fix prepared in ~20 minutes | One demo narrative, 06:10–08:13. | Example, not population-level MTTR. |
| Push-notification crash caught at 5% rollout; fixed the same day | One high-severity example, 08:22–09:02. | Not an aggregate regression-avoidance rate. |
| “Twofold” Jira resolution improvement | Speech is ambiguous: transcript says resolution time “increased,” while the speaker describes improvement. | Do not convert this into a precise 50% MTTR reduction without the actual metric definition and slide. |

The annual ~50,000 assigned issues and ~12,000 pages in the background section have different scope/time windows from monthly agent RCA volume. They cannot establish coverage by division. Descriptions/reposts with 5,000 monthly RCAs and 30% acceptance may reflect older summaries; they should not overwrite the local presentation's 9,000/48% figures or be combined into one measured cohort.

## Mapping to this assignment

| Assignment requirement | Fit shown by Uber | What still needs separate assignment work |
|---|---|---|
| Orchestrator and meaningful collaboration | Fixed harness; specialist fan-out; consolidation; state passed onward. | Explicit structured task/result contracts and dependency-aware coordination in our runnable prototype. |
| Observability agent | Logs, traces, session breadcrumbs, crash evidence. | The assignment also specifically requires a structured metrics query tool. |
| Dependency agent | Release correlation, version-bounded Git search, feature-flag context. | A service-dependency graph and deployment/configuration tools covering simulated services. |
| Reasoning agent | RCA categorization, confidence, consolidated specialist findings. | Ranked competing hypotheses with explicit support and contradiction records. |
| Critic agent | Validation tests can challenge a proposed repair. | No independently named critic or formal hypothesis-challenge loop is established. A testing node is not automatically the assignment's critic. |
| Reporting agent | Evidence timeline, RCA, PR and issue handoff. | Required final hypothesis ranking, facts versus assumptions, and inconclusive outcome. |
| Reliability | Per-node turn limits, bounded test retries, scoped context, execution traces. | Tool timeout/incomplete-result injection, agent crash recovery, aggregate budgets, and explicit termination semantics. |
| Evaluation | Production quality and adoption figures are described. | At least ten synthetic incidents and equal-tools single-agent comparison on accuracy, grounding, calls, latency, and tokens. No such controlled comparison was established here. |

## Lessons to consider later — not architecture decisions

1. Start from useful evidence contracts. Session/release identifiers and relevant intervals can make a specialist's job far narrower than a raw incident description.
2. Give each parallel investigator a concrete question and a scoped evidence set. Specialization needs operational meaning beyond changing a role prompt.
3. Preserve the provenance of evidence through consolidation. A timeline is useful only if each claim can be checked against its source.
4. Treat model turns, fan-out, tool retries, and validation retries as different budgets. Uber publishes some limits; an assignment implementation must make its own aggregate limits explicit and measured.
5. Keep domain instructions separate from execution machinery when that separation reduces maintenance. Runtime marketplace infrastructure itself would be disproportionate for a small assignment.
6. Measure exact RCA correctness separately from partial usefulness and repair acceptance. Each answers a different question.

## Unresolved details

No verified public schemas for shared state, subagent findings, confidence calibration, hypotheses, contradictions, or the consolidation algorithm. No complete tool API definitions, failure-recovery/checkpoint design, subagent conflict-resolution logic, token/cost distribution, equal-tools baseline, or public benchmark dataset. No evidence that confidence alone triggers abstention. These gaps are important because the assignment explicitly tests incomplete, misleading, contradictory, and unavailable evidence.
