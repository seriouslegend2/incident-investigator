# Live demo video: what to show

Open the actual application at `http://127.0.0.1:8000/` after starting it with:

```bash
cd incident-investigator
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The page starts a real background LangGraph investigation. It polls the durable case ledger, so the audit trail is live; it does not replay a stored answer. Use `email-confirmation-timeout` for the shortest clear first recording.

## Suggested 90-second recording

1. **0–10 seconds — complaint.** Show the selected scenario and the vague operator complaint. Say: “The operator has not provided logs, code or a diagnosis.”
2. **10–25 seconds — live coordination.** Click **Run live investigation**. Point to the audit trail as D1 plans and the selected D3–D6 specialists/tool receipts appear. Do not present the agents’ hidden reasoning as proof.
3. **25–40 seconds — traces.** Open the LangSmith project and filter by the displayed case ID. Show the individual root traces: `agent/d1/plan`, then parallel `agent/d3/investigate`, `agent/d4/investigate` and `agent/d6/investigate`, followed by D7 and D8. Open `agent/d3/investigate`: in **Inputs**, show the exact system prompt, D1-scoped task and D3's allowed tools; then expand its `tool/d3/...` child and show D3's structured output/handoff. The traces prove separate agent/model/tool calls occurred; the report cites the underlying evidence IDs.
4. **40–75 seconds — final D8 report.** Return to the local page. State clearly that this is the exact structured D8 output, released only after D7 reviewed the draft. Walk through: expected flow, observed flow, ranked hypotheses, evidence for/against, confidence, limitations and recommended actions.
5. **75–90 seconds — safety/uncertainty.** Point out that a report can be **WITHHELD** if D7 finds weak evidence. The system does not force a root cause.

## What the final viewer sees

- A concise D8 summary and D7 approval/withheld state.
- Expected flow versus observed flow.
- Up to five ranked explanations. Each includes a qualitative confidence, supporting evidence IDs, contradicting evidence IDs and missing evidence.
- Recommended next checks/actions and explicit limitations.
- A small agent/tool receipt timeline plus a link to the full LangSmith trace.

The viewer does **not** see raw chain-of-thought, whole codebases, database credentials or all log records. Those are neither necessary nor appropriate for a demo.
