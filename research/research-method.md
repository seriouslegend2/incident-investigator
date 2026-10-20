# How to interpret this research

Research date: 20 October 2026. This folder records the requested discovery phase: existing built systems relevant to the assignment, their available architecture, and lessons to discuss before selecting our architecture.

## Inputs reviewed

The main agent read the complete two-page assignment and the complete supplied Uber talk transcript. The Uber researcher also viewed both supplied screenshots. Three parallel researchers covered Uber/Meta, commercial investigation systems, and academic/open-source systems and benchmarks. The main agent added HolmesGPT, reviewed their notes, and assembled the comparison and HTML reading guide.

The original PDF, transcript, and screenshots are preserved in their existing locations. Every detailed case note names its sources and separates its evidence from interpretation.

## Evidence labels used in the notes

| Evidence type | What it establishes | What it does not establish |
| --- | --- | --- |
| Official engineering article or paper | The authors publicly describe an implemented design and results | Independent verification or current behavior of undisclosed production code |
| Official product documentation | An exposed feature or operating contract is documented | Internal implementation, historical availability, or performance guarantees |
| Inspected public source code | A particular checked path implements, omits or configures behavior | Successful execution, comprehensive correctness, or behavior of every released version |
| Supplied presentation transcript / slides | The speaker account and visible slide contents | Independent audit of deployment, complete API schemas, or ground-truth accuracy |
| Vendor/customer result | An attributed deployment or outcome claim | A controlled comparison generalizing to other incidents |
| Our interpretation / discussion question | A reasoned connection to the assignment | A feature or experiment actually implemented by the cited system |
| Unknown / not established | The reviewed evidence did not answer the question | Proof the feature does not exist |

## Search and selection method

Searches targeted first-party engineering accounts, official documentation, research papers, and author repositories. The team prioritized direct relevance and inspectable mechanisms: actual collaboration, hypothesis testing, critics, evidence provenance, execution reliability, and evaluation. Sources published after the research date were excluded. Secondary posts were useful only as locators, particularly for the Uber recording; they are labeled in that note.

The pack includes implemented research prototypes and non-agent investigation platforms when they illuminate a specific requirement. They are explicitly labeled so that code analyzers, sequential agents, and autonomous collaborating investigators are not treated as equivalent.

## What was verified and what was not

Public source code was read for HolmesGPT, mABC, ITBench agents, and selected benchmark evaluators. Several links are pinned to commits. The team did not install those systems, execute their benchmarks, access proprietary production environments, or independently reproduce reported performance. No final application architecture or framework was selected.

Live pages can change, and not every documentation page has a visible modification date. Each case ledger records access date and publication/version details when available. A date inconsistency in a Resolve article and an unavailable independent Uber transcript fetch are recorded rather than silently resolved.

## Important findings about evidence quality

- [mABC](systems/mabc-multi-agent-rca.md): the checked runner disables the described voting call and does not visibly enforce the paper's step cap in that path. A paper table and prose also disagree. These details need reconciliation before treating the artifact as a complete reference implementation.
- [ITBench](systems/ibm-itbench-sre-agent.md): archived CrewAI agents and the replacement framework differ. Old benchmark scores cannot be assigned to the current architecture.
- [Uber](systems/uber-debug-assist.md): partial usefulness is not exact correctness; PR acceptance is not all-incident resolution. Future specialist-count projections are not achieved scale.
- [Commercial products](comparison.md): agent names and diagrams expose only part of the design. Missing retry, state, or confidence details remain open.

## Packaging

The main reading file is `index.html`, maintained as a self-contained guide. Current user-established scope is synchronized in `system-requirements.md`, including vague-input discovery, codebase, actual database contents, infrastructure, and AI application prompt/context/tool/coordination investigation. Historical company case notes describe their sources; they should not be read as the full current scope.

The optional `detailed-research.html` archive embeds the Markdown notes with local navigation and search, without external JavaScript libraries. Links to original local material require retaining the workspace files; online sources require network access. Published articles are summarized and linked, not mirrored in full.

Rebuild after editing notes with `node research/build-overview.mjs` from the workspace root. The build script performs a deterministic local formatting operation and does not fetch online content. Its small Markdown renderer supports the structures used in this pack; it is not a general Markdown engine.
