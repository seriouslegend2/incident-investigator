"""Small local-only presentation page for the real investigation API."""

DEMO_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Incident Investigator — Live Demo</title>
  <style>
    :root { --navy:#11223b; --ink:#1d2a3b; --muted:#64748b; --line:#dbe3ee; --bg:#f4f7fb; --card:#fff; --blue:#2563eb; --green:#087f5b; --amber:#a16207; --red:#b42318; }
    * { box-sizing:border-box; } body { margin:0; background:var(--bg); color:var(--ink); font:15px/1.5 Inter,ui-sans-serif,system-ui,sans-serif; }
    main { width:min(1180px, calc(100% - 32px)); margin:0 auto; padding:32px 0 64px; } h1 { font-size:30px; margin:0; } h2 { font-size:19px; margin:0 0 12px; } h3 { font-size:15px; margin:0 0 7px; } p { margin:7px 0; } .muted { color:var(--muted); }.top { display:flex; justify-content:space-between; gap:20px; align-items:start; margin-bottom:22px; }.badge { display:inline-block; border-radius:999px; padding:4px 10px; font-size:12px; font-weight:700; }.ready { background:#dcfce7; color:#166534; }.running { background:#dbeafe; color:#1d4ed8; }.withheld,.failed { background:#fee2e2; color:var(--red); }.open { background:#fef3c7; color:var(--amber); }.card { background:var(--card); border:1px solid var(--line); border-radius:14px; padding:18px; box-shadow:0 1px 2px #0f172a08; }.controls { display:grid; grid-template-columns:1fr 1fr auto; gap:12px; align-items:end; }.controls label { display:block; font-size:12px; font-weight:700; color:var(--muted); margin-bottom:4px; } select,input,button { width:100%; font:inherit; } select,input { border:1px solid #bdc9d8; border-radius:8px; min-height:42px; padding:9px 11px; background:white; } button { min-height:42px; padding:9px 18px; border:0; border-radius:8px; background:var(--blue); color:white; font-weight:700; cursor:pointer; } button:disabled { opacity:.6; cursor:wait; }.status-line { margin-top:14px; padding:10px 12px; background:#eff6ff; border-left:4px solid var(--blue); color:#1e3a5f; }.layout { display:grid; grid-template-columns:minmax(0,2fr) minmax(280px,1fr); gap:18px; margin-top:18px; }.report { display:grid; gap:14px; }.headline { display:flex; flex-wrap:wrap; align-items:center; gap:10px; }.case { color:var(--muted); font:12px ui-monospace,SFMono-Regular,Menlo,monospace; }.flow { display:grid; grid-template-columns:1fr 1fr; gap:12px; }.flow section { padding:13px; border-radius:10px; background:#f8fafc; border:1px solid var(--line); }.flow ol,.actions,.limits { padding-left:20px; margin:7px 0 0; }.hypothesis { border:1px solid var(--line); border-radius:10px; padding:13px; margin-top:9px; }.hypothesis p { margin:4px 0; }.pill { display:inline-block; padding:2px 7px; margin-left:5px; border-radius:99px; font-size:11px; font-weight:700; background:#e8effa; color:#285286; }.evidence { font:12px ui-monospace,SFMono-Regular,Menlo,monospace; color:#334155; }.timeline { max-height:560px; overflow:auto; }.event { padding:10px 0 10px 13px; border-left:2px solid #bfdbfe; position:relative; }.event:before { content:""; position:absolute; width:8px; height:8px; background:var(--blue); border-radius:50%; left:-5px; top:15px; }.event strong { display:block; font-size:13px; }.event span { color:var(--muted); font-size:12px; }.event .ok { color:var(--green); }.event .bad { color:var(--red); }.report-section { border-top:1px solid var(--line); padding-top:12px; }.trace { display:inline-block; margin-top:8px; color:var(--blue); font-weight:700; text-decoration:none; }.hidden { display:none; }.error { color:var(--red); }.small { font-size:13px; } @media(max-width:780px) { .controls,.layout,.flow { grid-template-columns:1fr; } .top { display:block; } }
    /* Each audit item deliberately answers: input → output → next step. */
    .timeline { max-height:720px; overflow:auto; padding-right:3px; }
    .event { padding:12px 0 14px 15px; border-left:2px solid #bfdbfe; position:relative; }
    .event:before { content:""; position:absolute; width:8px; height:8px; background:var(--blue); border-radius:50%; left:-5px; top:17px; }
    .event p { margin:6px 0; font-size:12px; }
    .event-key { color:var(--muted); font-weight:700; display:inline-block; min-width:66px; }
    .layout { grid-template-columns:minmax(0,1.45fr) minmax(400px,1fr); }
    .agent-card { margin:0 0 14px; padding:13px; border:1px solid var(--line); border-radius:11px; background:#fbfdff; }
    .agent-head { display:flex; justify-content:space-between; gap:8px; align-items:start; padding-bottom:9px; border-bottom:1px solid var(--line); }
    .agent-title { font-size:14px; font-weight:800; }.agent-purpose { display:block; color:var(--muted); font-size:12px; margin-top:2px; }
    .audit-row { margin:9px 0; font-size:12px; }.audit-key { display:block; color:var(--muted); font-size:10px; font-weight:800; letter-spacing:.04em; text-transform:uppercase; margin-bottom:2px; }
    .tool-group { margin-top:11px; padding:10px; background:#f1f5f9; border-radius:8px; }.tool-group h4 { margin:0 0 8px; font-size:12px; }
    .tool-card { margin-top:7px; padding:8px; background:#fff; border:1px solid #dbe3ee; border-radius:7px; font-size:12px; }.tool-card:first-of-type { margin-top:0; }
    .tool-card strong { display:block; }.tool-purpose { color:var(--muted); margin-top:2px; }.no-tool { margin-top:11px; padding:8px; border-radius:7px; background:#f8fafc; color:var(--muted); font-size:12px; }
    .citation-list { margin-top:9px; padding-top:8px; border-top:1px dashed var(--line); }
  </style>
</head>
<body>
<main>
  <div class="top">
    <div><h1>Incident Investigator</h1><p class="muted">Live LangGraph investigation → D7 final review → actual D8 report</p></div>
    <span id="caseStatus" class="badge open">READY FOR A LIVE CASE</span>
  </div>

  <section class="card">
    <form id="investigationForm">
      <div class="controls">
        <div><label for="scenario">DEMO SCENARIO</label><select id="scenario" required></select></div>
        <div><label for="complaint">OPERATOR COMPLAINT</label><input id="complaint" minlength="8" required></div>
        <div><button id="runButton" type="submit">Run live investigation</button></div>
      </div>
    </form>
    <div id="statusLine" class="status-line">Choose a scenario. The report will be generated by real model calls, not looked up from fixture data.</div>
  </section>

  <section class="layout">
    <article id="reportCard" class="card report hidden" aria-live="polite">
      <div class="headline"><h2>D8 final incident report</h2><span id="reportStatus" class="badge"></span></div>
      <div id="caseId" class="case"></div>
      <section><h3>Summary</h3><p id="summary"></p></section>
      <section class="flow"><section><h3>Expected flow</h3><ol id="expected"></ol></section><section><h3>Observed flow</h3><ol id="observed"></ol></section></section>
      <section><h3>Ranked hypotheses</h3><div id="hypotheses"></div></section>
      <section><h3>Conclusion</h3><p id="conclusion"></p></section>
      <section><h3>Recommended next steps</h3><ol id="actions" class="actions"></ol></section>
      <section><h3>Limitations / unresolved evidence</h3><ul id="limitations" class="limits"></ul></section>
      <section><h3>Evidence-cited sections</h3><div id="sections"></div></section>
      <a id="traceLink" class="trace hidden" target="_blank" rel="noreferrer">Open this live case in LangSmith ↗</a>
    </article>

    <aside class="card"><h2>Multi-agent collaboration</h2><p class="muted small">Separate agents exchange only structured tasks, findings and citations. They do not share one unrestricted prompt.</p><div id="collaborationFlow" class="no-tool">Start a case to see the agents selected by D1.</div><div id="timeline" class="timeline"><p class="muted">No case started.</p></div></aside>
  </section>
</main>
<script>
  const state = { caseId: null, timer: null };
  const $ = (id) => document.getElementById(id);
  const AGENT_INFO = {
    D1: { name: "D1 — investigation coordinator", purpose: "Turns the complaint and evidence gaps into scoped tasks. It has no raw log, code or database tool.", action: "planned the next investigation batch" },
    D3: { name: "D3 — observability investigator", purpose: "Checks bounded traces, logs and metrics for what happened at runtime.", action: "investigated runtime observations" },
    D4: { name: "D4 — code and deployment investigator", purpose: "Checks approved code snippets, revisions, deployment and configuration facts.", action: "mapped code and deployment behavior" },
    D5: { name: "D5 — read-only data investigator", purpose: "Checks only backend-approved rows/history through a cited data contract.", action: "checked bounded read-only data" },
    D6: { name: "D6 — AI behavior investigator", purpose: "Checks retained AI-run, prompt, retrieval, tool and handoff records.", action: "checked AI runtime behavior" },
    D7: { name: "D7 — independent critic", purpose: "Challenges scope, citations, contradictions and overconfident claims. It has no source tools.", action: "reviewed the evidence or exact draft" },
    D8: { name: "D8 — final report writer", purpose: "Writes only from D7-reviewed findings. It has no source tools and cannot approve itself.", action: "wrote the structured incident report" }
  };
  const TOOL_INFO = {
    find_trace_or_request: "Finds one bounded correlated request or trace.", search_log_slice: "Reads a narrow time/service log slice.", get_metric_or_provider_window: "Checks a limited metric or provider-result window.",
    map_service_path: "Maps a candidate service and dependency path.", search_code_symbols: "Searches approved code symbols.", read_source_range: "Reads a small approved source range.", get_deployment_or_config_diff: "Checks bounded deployment or configuration facts.",
    describe_authorized_projection: "Describes the allowed read-only data projection.", lookup_contract_row: "Looks up one contract-scoped row.", get_contract_history: "Reads bounded history for that contract.",
    get_ai_run_trace: "Reads a retained AI-run timeline.", get_prompt_snapshot: "Reads a redacted prompt snapshot.", get_retrieval_snapshot: "Reads retrieval context.", get_tool_handoff_timeline: "Reads AI tool/handoff timing."
  };
  const escapeHtml = (value) => String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll(String.fromCharCode(34), "&quot;").replaceAll("'", "&#39;");
  const list = (items) => (items || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("") || "<li>None recorded.</li>";
  const statusClass = (status) => ["delivered", "succeeded", "approved"].includes(status) ? "ready" : ["withheld", "failed", "rejected"].includes(status) ? "failed" : ["investigating", "reviewing", "started"].includes(status) ? "running" : "open";
  function setStatus(status, text) { const node = $("caseStatus"); node.className = `badge ${statusClass(status)}`; node.textContent = text; }
  function scenarioText(item) { return `${item.title} — ${item.description}`; }
  async function loadScenarios() {
    const response = await fetch("/api/demo/scenarios");
    if (!response.ok) throw new Error("The API is unavailable. Configure the demo database and OpenAI key first.");
    const scenarios = await response.json();
    $("scenario").innerHTML = scenarios.map((item) => `<option value="${escapeHtml(item.scenario_id)}" data-description="${escapeHtml(item.description)}">${escapeHtml(item.title)}</option>`).join("");
    $("complaint").value = scenarios[0]?.description || "";
    $("scenario").addEventListener("change", () => { const selected = scenarios.find((item) => item.scenario_id === $("scenario").value); $("complaint").value = selected?.description || ""; });
  }
  function renderCollaborationFlow(agents) {
    const specialistRoles = [...new Set(agents.filter((event) => event.label.endsWith("· investigate")).map((event) => event.role))];
    const hasD8 = agents.some((event) => event.role === "D8");
    const finalReview = agents.some((event) => event.role === "D7" && event.label.endsWith("review_report"));
    const specialistText = specialistRoles.length ? specialistRoles.join(" + ") : "no specialist completed yet";
    $("collaborationFlow").innerHTML = `<strong>D1</strong> delegates in parallel to <strong>[ ${escapeHtml(specialistText)} ]</strong> → <strong>D7 evidence review</strong>${hasD8 ? " → <strong>D8 report</strong>" : ""}${finalReview ? " → <strong>D7 final gate</strong> → <strong>operator</strong>" : ""}`;
  }
  function renderTimeline(events) {
    const agents = events.filter((event) => event.kind === "agent");
    const toolsByAgent = new Map();
    for (const event of events.filter((item) => item.kind === "tool")) {
      const tools = toolsByAgent.get(event.parent_event_id) || []; tools.push(event); toolsByAgent.set(event.parent_event_id, tools);
    }
    renderCollaborationFlow(agents);
    $("timeline").innerHTML = agents.length ? agents.map((agent) => {
      const info = AGENT_INFO[agent.role] || { name: agent.label, purpose: "Bounded investigation role.", action: "performed its assigned operation" };
      const tools = toolsByAgent.get(agent.event_id) || [];
      const toolMarkup = tools.length ? `<div class="tool-group"><h4>Tool calls made by this agent</h4>${tools.map((tool) => `<div class="tool-card"><strong>${escapeHtml(tool.label.replace(`${tool.role} · `, ""))} <span class="${tool.status === "failed" ? "bad" : tool.status === "succeeded" ? "ok" : ""}">${escapeHtml(tool.status)}</span></strong><div class="tool-purpose">${escapeHtml(TOOL_INFO[tool.label.replace(`${tool.role} · `, "")] || "Bounded source read.")}</div><p><span class="event-key">INPUT</span>${escapeHtml(tool.input_summary)}</p><p><span class="event-key">RESULT</span>${escapeHtml(tool.output_summary)}</p></div>`).join("")}</div>` : `<div class="no-tool">${["D1", "D7", "D8"].includes(agent.role) ? "No source tool by design for this role." : "No source tool call was needed or completed for this task."}</div>`;
      return `<article class="agent-card"><div class="agent-head"><div><span class="agent-title">${escapeHtml(info.name)}</span><span class="agent-purpose">${escapeHtml(info.purpose)}</span></div><span class="${agent.status === "failed" ? "bad" : agent.status === "succeeded" ? "ok" : ""}">${escapeHtml(agent.status)}</span></div><div class="audit-row"><span class="audit-key">Received</span>${escapeHtml(agent.input_summary)}</div><div class="audit-row"><span class="audit-key">What it did</span>${escapeHtml(info.action)}</div>${toolMarkup}<div class="audit-row"><span class="audit-key">Returned</span>${escapeHtml(agent.output_summary)}</div>${agent.evidence_ids?.length ? `<div class="citation-list evidence">Evidence IDs: ${escapeHtml(agent.evidence_ids.join(", "))}</div>` : ""}<div class="audit-row"><span class="audit-key">Handoff / next step</span>${escapeHtml(agent.next_step)}</div></article>`;
    }).join("") : `<p class="muted">Waiting for D1 to create the first agent task…</p>`;
  }
  function renderReport(report, incidentCase, traceUrl) {
    $("reportCard").classList.remove("hidden");
    $("reportStatus").className = `badge ${statusClass(report.status)}`;
    $("reportStatus").textContent = report.status === "delivered" && report.reviewed_by_d7 ? "D7 APPROVED" : "WITHHELD";
    $("caseId").textContent = `Case ${incidentCase.case_id} · scenario ${incidentCase.scope.scenario_id}`;
    $("summary").textContent = report.summary;
    $("expected").innerHTML = list(report.expected_flow);
    $("observed").innerHTML = list(report.observed_flow);
    $("conclusion").textContent = report.conclusion;
    $("actions").innerHTML = list(report.recommended_next_steps);
    $("limitations").innerHTML = list(report.limitations);
    $("hypotheses").innerHTML = (report.ranked_hypotheses || []).map((item) => `<article class="hypothesis"><strong>#${item.rank} ${escapeHtml(item.statement)}</strong><p><span class="pill">${escapeHtml(item.assessment)}</span><span class="pill">${escapeHtml(item.confidence)} confidence</span></p><p class="evidence">Supports: ${escapeHtml((item.supporting_evidence_ids || []).join(", ") || "none")} · Contradicts: ${escapeHtml((item.contradicting_evidence_ids || []).join(", ") || "none")}</p><p class="small">Missing: ${escapeHtml((item.missing_evidence || []).join("; ") || "none recorded")}</p></article>`).join("");
    $("sections").innerHTML = (report.sections || []).map((item) => `<section class="report-section"><h3>${escapeHtml(item.title)}</h3><p>${escapeHtml(item.text)}</p><p class="evidence">Evidence: ${escapeHtml((item.evidence_ids || []).join(", ") || "none")}</p></section>`).join("");
    if (traceUrl) { $("traceLink").href = traceUrl; $("traceLink").classList.remove("hidden"); }
  }
  async function pollCase() {
    if (!state.caseId) return;
    const [caseResponse, timelineResponse] = await Promise.all([fetch(`/api/investigations/${state.caseId}`), fetch(`/api/investigations/${state.caseId}/timeline`)]);
    if (!caseResponse.ok || !timelineResponse.ok) throw new Error("Could not read the live case status.");
    const payload = await caseResponse.json();
    renderTimeline(await timelineResponse.json());
    const stateText = payload.case.status.replaceAll("_", " ").toUpperCase();
    setStatus(payload.case.status, stateText);
    if (payload.report) {
      renderReport(payload.report, payload.case, payload.trace_url);
      $("statusLine").textContent = payload.report.status === "delivered" ? "D8 created this final report and D7 approved its exact content." : "D7 withheld the final report because the available evidence was not sufficient.";
      $("runButton").disabled = false;
      $("runButton").textContent = "Run live investigation";
      clearInterval(state.timer); state.timer = null;
    }
  }
  $("investigationForm").addEventListener("submit", async (event) => {
    event.preventDefault(); clearInterval(state.timer); $("reportCard").classList.add("hidden"); $("traceLink").classList.add("hidden");
    $("runButton").disabled = true; $("runButton").textContent = "Agents are investigating…"; setStatus("investigating", "LIVE INVESTIGATION");
    $("statusLine").textContent = "D1 is selecting evidence specialists. The audit trail will update as agent and tool receipts are persisted.";
    try {
      const response = await fetch("/api/investigations/start", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ scenario_id: $("scenario").value, complaint: $("complaint").value, requested_by: "live-demo" }) });
      const payload = await response.json(); if (!response.ok) throw new Error(payload.detail || "Could not start investigation.");
      state.caseId = payload.case.case_id; await pollCase(); state.timer = setInterval(() => pollCase().catch(showError), 1500);
    } catch (error) { showError(error); }
  });
  function showError(error) { clearInterval(state.timer); $("runButton").disabled = false; $("runButton").textContent = "Run live investigation"; setStatus("failed", "DEMO ERROR"); $("statusLine").innerHTML = `<span class=\"error\">${escapeHtml(error.message || error)}</span>`; }
  loadScenarios().catch(showError);
</script>
</body>
</html>"""
