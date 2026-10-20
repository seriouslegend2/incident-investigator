# Evaluation plan and results ledger

## Fair comparison

Compare two approaches on the same 11 scenario inputs:

| Control | Multi-agent system | Single-agent baseline |
| --- | --- | --- |
| Model/provider | Same | Same |
| Complaint and scenario | Same | Same |
| Source access | Same bounded evidence tools | Same bounded evidence tools |
| Tool limits/failure replay | Same | Same |
| Hidden evaluator key | Never visible to agents | Never visible to the agent |
| Output contract | Same structured report fields | Same structured report fields |

The baseline is one model that chooses among the same source-specific tools and writes the same report. It must not be a shortcut that receives a curated evidence bundle or the multi-agent conclusion.

## Metrics

| Metric | Method |
| --- | --- |
| Root-cause accuracy | Evaluator compares the reported primary mechanism/component with a hidden answer key and predefined acceptable alternatives. |
| Evidence grounding | Score each material claim for cited support, valid scope/time/revision, and treatment of counterevidence. |
| Tool-call count | Count every attempted call, including empty, partial, timeout and retry. |
| Latency | Wall-clock time from submitted complaint to final report. Keep branch timing so parallel work is not summed as serial time. |
| Token consumption | Sum input/output model usage across every agent/model invocation and retry. |

## Result table

No comparative run has been recorded yet. This empty ledger is intentional: numbers must be produced by the evaluator rather than invented in documentation.

| System | Cases | Accuracy | Grounding | Tool calls | Median latency | Total tokens | Run artifact |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Multi-agent | — | — | — | — | — | — | Not run |
| Single-agent baseline | — | — | — | — | — | — | Not built / not run |

## Required next run

1. Implement the baseline, hidden scoring key, timeout/partial replay and report-field schema.
2. Run every scenario under both systems with a fixed model/version and identical call limits.
3. Save per-case machine-readable results, LangSmith root-trace URL, elapsed time, token usage and tool receipts.
4. Aggregate the table above; include failures and inconclusive reports rather than discarding them.
5. Add automated regression assertions for report schema, no-answer leakage, failure semantics and metric collection.
