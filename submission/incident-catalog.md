# Synthetic incident catalogue

Each incident begins with only the operator’s complaint. The source records are seeded in `incident-investigator/app/db/demo_seed.py` and are retrieved only through the agents’ bounded tools. This catalogue describes what was injected for test coverage; it does **not** provide a root-cause answer to the runtime.

Run any case with:

```bash
cd incident-investigator
uv run python scripts/run_case.py <scenario-id> "<operator complaint>"
```

| # | Scenario ID | Operator complaint | Injected evidence families | What the case is designed to test |
| --- | --- | --- | --- | --- |
| 1 | `email-confirmation-timeout` | Completed order, but no confirmation email | Correlated checkout/email logs; bounded provider window; delivery-event row | Trace correlation, downstream timeout, and a limited absence claim. |
| 2 | `message-reminder` | A group missed an afternoon reminder | Request/worker logs; sender code path; deployment metadata; recipient preference row | Code-to-data contract, a null recipient field, and deploy timing. |
| 3 | `tax-total` | Checkout tax looks too high | Checkout log; tax-rule code path; deployment; payment history | Data-driven business rule selection and multiple matching rule identifiers. |
| 4 | `ai-policy-cache` | Assistant used an old policy | App trace; AI retrieval/prompt records; policy-service cache configuration | AI retrieval freshness versus configuration. |
| 5 | `payment-status` | Payment shows failed after a charge | Webhook retry and state-transition logs; handler code; payment row | External delivery retry, internal state transition and conflicting statuses. |
| 6 | `tenant-cache` | User saw another tenant’s cached value | Request/response correlation; cache-key code path; deployment | Tenant-isolation impact and a code-level cache-key hypothesis. |
| 7 | `ai-duplicate-booking` | One conversation made two booking requests | Two AI tool events; callback timeout; idempotency code note; duplicate event rows | AI tool timeline, retry behavior and duplicate-effect data. |
| 8 | `inventory-replay` | Stock became negative after retry | Re-delivered consumer event; consumer code; compacted/partial history | Event replay and the distinction between partial retained history and proof. |
| 9 | `api-latency` | Customer-facing API became slow | Latency metric; low trace sampling/gap; completed deployment | A performance issue with incomplete telemetry, so the report may need to be inconclusive. |
| 10 | `timezone-history` | Scheduled message was sent at wrong local time | Scheduler trigger; schedule-creation code; retained schedule row | UTC versus customer-time-zone behavior and historical state. |
| 11 | `search-locale` | Results ignore selected locale | Search request; locale-selection code; AI query-rewrite run | Cross-domain investigation between app code and AI execution. |

## Coverage matrix

| Stressor | Cases |
| --- | --- |
| Code/application behavior | 2, 3, 5, 6, 7, 8, 10, 11 |
| Deployment/config correlation | 2, 3, 4, 6, 9 |
| Data or retained history | 1, 2, 3, 5, 7, 8, 10 |
| AI prompt/retrieval/tool behavior | 4, 7, 11 |
| Conflicting or misleading observations | 3, 5, 8, 9 |
| Deliberately incomplete source coverage | 1, 8, 9 |

The assignment also requires actual simulated tool failures such as timeouts. The current data contains incomplete evidence (for example, retained history or trace gaps), but not yet gateway-level timeout/unavailable replay. That is a known implementation item, not a completed claim.

## Rules for future answer keys

- Store expected causes and acceptable alternatives in an evaluator-only file or secured evaluator table.
- Do not add an answer field to `DEMO_SCENARIOS`, tool output, prompts or the report writer context.
- Score a case from the final cited report and tool receipts, not from a free-text similarity score alone.
- Permit an inconclusive result when the scenario intentionally does not establish causation.
