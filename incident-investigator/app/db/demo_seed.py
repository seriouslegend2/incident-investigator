from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .database import Database


def _at(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=UTC)


# Every scenario has raw, imperfect signals from independent source types.  None stores an
# expected root cause or pre-written incident report; the agents must search and interpret it.
DEMO_SCENARIOS: list[dict[str, Any]] = [
    {
        "scenario_id": "email-confirmation-timeout",
        "title": "Order confirmation email was not received",
        "description": "A customer says their completed order did not receive a confirmation email.",
        "records": [
            (
                "observability",
                "otel-log-001",
                "2026-10-20T09:15:00",
                "Checkout order completed",
                "trace_id=trace-42 order_id=order-42 customer_id=customer-42 service=checkout event=order.completed",
                "simulated OpenTelemetry checkout trace; correlation fields retained",
            ),
            (
                "observability",
                "otel-log-002",
                "2026-10-20T09:15:01",
                "Confirmation HTTP request timed out",
                "trace_id=trace-42 order_id=order-42 service=checkout downstream=email route=send_order_confirmation timeout_ms=1000 error=context deadline exceeded",
                "simulated correlated checkout/email trace slice",
            ),
            (
                "observability",
                "otel-log-003",
                "2026-10-20T09:15:02",
                "Provider receipt absent in bounded window",
                "trace_id=trace-42 order_id=order-42 service=email metric=demo.notification.confirmations value=0 window_seconds=120",
                "simulated bounded provider and metric window; does not prove all provider history",
            ),
            (
                "data",
                "otel-data-001",
                "2026-10-20T09:15:03",
                "Delivery event history",
                "relation=delivery_events customer_id=customer-42 order_id=order-42 event_type=confirmation_requested provider_receipt=null observed_at=2026-10-20T09:15:00Z",
                "simulated read replica; one bounded event row; lag 2 seconds",
            ),
        ],
    },
    {
        "scenario_id": "message-reminder",
        "title": "Customer reminder missing",
        "description": "A customer says their group did not receive the afternoon reminder.",
        "records": [
            (
                "observability",
                "log-101",
                "2026-10-19T09:01:10",
                "Reminder request accepted",
                "request_id=req-91 message_id=msg-440 group=customer-a event=reminder.accepted",
                "demo log slice 09:00–09:10",
            ),
            (
                "observability",
                "log-102",
                "2026-10-19T09:01:14",
                "Worker send attempt failed",
                "request_id=req-91 message_id=msg-440 provider_status=400 error=destination must not be empty",
                "demo worker log slice 09:00–09:10",
            ),
            (
                "code_deploy",
                "code-101",
                "2026-10-19T08:30:00",
                "Reminder sender deployed",
                "service=notification-worker revision=7bc12 path=workers/reminders.py function=send_reminder reads customer_preferences.notification_destination then enqueues provider request",
                "demo repository index at revision 7bc12",
            ),
            (
                "code_deploy",
                "deploy-101",
                "2026-10-19T08:35:00",
                "Worker deployment metadata",
                "service=notification-worker environment=demo image=notification-worker:7bc12 config_hash=cfg-55",
                "demo deployment ledger",
            ),
            (
                "data",
                "data-101",
                "2026-10-19T09:01:13",
                "Preference row for message recipient",
                "relation=customer_preferences customer_id=cust-18 notification_destination=null updated_at=2026-10-19T08:58:00",
                "demo read replica; 1 row; lag 2 seconds",
            ),
        ],
    },
    {
        "scenario_id": "tax-total",
        "title": "Checkout tax total appears wrong",
        "description": "A customer says the tax on a checkout is higher than expected.",
        "records": [
            (
                "observability",
                "log-201",
                "2026-10-19T11:20:00",
                "Checkout completed",
                "order_id=ord-77 jurisdiction=KA subtotal=1000 tax_total=180 status=paid",
                "demo API and payment trace",
            ),
            (
                "code_deploy",
                "code-201",
                "2026-10-19T10:50:00",
                "Tax rules code path",
                "service=checkout-api revision=1fd28 path=pricing/tax.py function=apply_tax chooses active tax_rules by jurisdiction and effective_at",
                "demo repository index at revision 1fd28",
            ),
            (
                "code_deploy",
                "deploy-201",
                "2026-10-19T11:00:00",
                "Pricing deployment metadata",
                "service=checkout-api environment=demo image=checkout:1fd28 config_hash=cfg-88",
                "demo deployment ledger",
            ),
            (
                "data",
                "data-201",
                "2026-10-19T11:20:00",
                "Tax rule window",
                "relation=payment_attempts payment_id=pay-77 order_id=ord-77 tax_rule_ids=[KA-STD,KA-FESTIVE] tax_total=180",
                "demo history replica; 1 row; lag 3 seconds",
            ),
        ],
    },
    {
        "scenario_id": "ai-policy-cache",
        "title": "Assistant used an old policy",
        "description": "An operator reports that an AI assistant gave policy guidance that had changed.",
        "records": [
            (
                "observability",
                "log-301",
                "2026-10-19T13:02:00",
                "Assistant response delivered",
                "conversation_id=conv-33 run_id=ai-900 status=completed latency_ms=1100",
                "demo application trace",
            ),
            (
                "ai_runtime",
                "ai-301",
                "2026-10-19T13:01:59",
                "AI retrieval context",
                "run_id=ai-900 prompt_version=helpdesk-v4 model=gpt-4.1-mini retrieval_document=refund-policy-v2 retrieval_cached_at=2026-10-10",
                "demo AI run ledger",
            ),
            (
                "ai_runtime",
                "ai-302",
                "2026-10-19T13:02:00",
                "AI tool and output event",
                "run_id=ai-900 tool_calls=[] response_references=refund policy version 2",
                "demo AI run ledger",
            ),
            (
                "code_deploy",
                "deploy-301",
                "2026-10-18T18:00:00",
                "Policy service deployment",
                "service=policy-search environment=demo revision=9ae11 config_hash=cfg-92 cache_ttl_seconds=86400",
                "demo deployment metadata",
            ),
        ],
    },
    {
        "scenario_id": "payment-status",
        "title": "Payment marked failed after charge",
        "description": "Support sees a payment failure even though the customer says money was taken.",
        "records": [
            (
                "observability",
                "log-401",
                "2026-10-19T14:45:00",
                "Webhook retry",
                "payment_id=pay-44 provider_event=charge.captured delivery_attempt=2 response_status=500",
                "demo webhook logs",
            ),
            (
                "observability",
                "log-402",
                "2026-10-19T14:45:03",
                "Order status transition",
                "payment_id=pay-44 order_id=ord-44 transition=pending_to_failed actor=webhook-consumer",
                "demo event trace",
            ),
            (
                "code_deploy",
                "code-401",
                "2026-10-19T14:10:00",
                "Webhook handler path",
                "service=payments-worker revision=3d71 path=webhooks/charges.py function=handle_charge captures provider event then updates payment_attempts",
                "demo repository index",
            ),
            (
                "data",
                "data-401",
                "2026-10-19T14:45:05",
                "Payment attempt history",
                "relation=payment_attempts payment_id=pay-44 provider_status=captured internal_status=failed updated_at=2026-10-19T14:45:03",
                "demo history replica; 1 row; lag 1 second",
            ),
        ],
    },
    {
        "scenario_id": "tenant-cache",
        "title": "Customer sees another tenant's cached value",
        "description": "A user says a screen displayed data that did not belong to their account.",
        "records": [
            (
                "observability",
                "log-501",
                "2026-10-19T15:05:00",
                "Cache hit",
                "request_id=req-501 tenant=tenant-a cache_key=profile:42 cache_hit=true",
                "demo API trace",
            ),
            (
                "observability",
                "log-502",
                "2026-10-19T15:05:00",
                "Response correlation",
                "request_id=req-501 response_customer_id=cust-b42 tenant=tenant-a",
                "demo API trace",
            ),
            (
                "code_deploy",
                "code-501",
                "2026-10-19T14:55:00",
                "Profile cache code path",
                "service=profile-api revision=4e201 path=cache/profile.py function=build_key uses profile:{user_id}",
                "demo repository index",
            ),
            (
                "code_deploy",
                "deploy-501",
                "2026-10-19T15:00:00",
                "Profile API deployment",
                "service=profile-api environment=demo image=profile:4e201 config_hash=cfg-07",
                "demo deployment ledger",
            ),
        ],
    },
    {
        "scenario_id": "ai-duplicate-booking",
        "title": "AI assistant created duplicate booking requests",
        "description": "An operator reports two booking requests after one customer conversation.",
        "records": [
            (
                "ai_runtime",
                "ai-601",
                "2026-10-19T16:01:00",
                "First booking tool call",
                "run_id=ai-601 conversation_id=conv-61 tool=create_booking arguments_hash=arg-1 result=booking-900",
                "demo AI run ledger",
            ),
            (
                "ai_runtime",
                "ai-602",
                "2026-10-19T16:01:04",
                "Second booking tool call",
                "run_id=ai-601 conversation_id=conv-61 tool=create_booking arguments_hash=arg-1 result=booking-901",
                "demo AI run ledger",
            ),
            (
                "observability",
                "log-601",
                "2026-10-19T16:01:03",
                "Tool callback timeout",
                "run_id=ai-601 tool_call=create_booking callback_timeout_ms=3000 retry=true",
                "demo orchestration trace",
            ),
            (
                "code_deploy",
                "code-601",
                "2026-10-19T15:40:00",
                "Booking tool integration",
                "service=booking-agent revision=8a922 path=tools/bookings.py function=create_booking forwards idempotency_key when provided",
                "demo repository index",
            ),
            (
                "data",
                "data-601",
                "2026-10-19T16:01:05",
                "Booking event rows",
                "relation=delivery_events customer_id=cust-61 event_types=[booking_created,booking_created] correlation_id=conv-61",
                "demo history replica; 2 rows; lag 1 second",
            ),
        ],
    },
    {
        "scenario_id": "inventory-replay",
        "title": "Inventory became negative",
        "description": "A warehouse dashboard shows a negative stock count after a retry.",
        "records": [
            (
                "observability",
                "log-701",
                "2026-10-19T17:01:00",
                "Inventory event consumed",
                "event_id=evt-700 sku=rice-5kg delta=-1 delivery_attempt=1",
                "demo consumer trace",
            ),
            (
                "observability",
                "log-702",
                "2026-10-19T17:01:20",
                "Inventory event redelivered",
                "event_id=evt-700 sku=rice-5kg delta=-1 delivery_attempt=2 cause=consumer_ack_timeout",
                "demo consumer trace",
            ),
            (
                "code_deploy",
                "code-701",
                "2026-10-19T16:45:00",
                "Inventory consumer path",
                "service=inventory-worker revision=6f711 path=consumers/inventory.py function=apply_delta records inventory_events then updates stock",
                "demo repository index",
            ),
            (
                "data",
                "data-701",
                "2026-10-19T17:01:22",
                "Inventory history coverage",
                "relation=inventory_events sku=rice-5kg visible_events=1 retention_note=hourly compaction pending",
                "demo history replica; partial history; lag 4 seconds",
            ),
        ],
    },
    {
        "scenario_id": "api-latency",
        "title": "API became slow",
        "description": "A customer-facing API is reported slow during afternoon traffic.",
        "records": [
            (
                "observability",
                "log-801",
                "2026-10-19T18:00:00",
                "Latency metric",
                "service=search-api p95_ms=4200 baseline_p95_ms=280 request_count=1400",
                "demo metrics sample 17:55–18:05",
            ),
            (
                "observability",
                "log-802",
                "2026-10-19T18:01:00",
                "Trace gap",
                "service=search-api trace_sampling=0.1 correlated_db_spans=unavailable",
                "demo telemetry configuration",
            ),
            (
                "code_deploy",
                "deploy-801",
                "2026-10-19T17:35:00",
                "Search API deployment",
                "service=search-api environment=demo image=search:2ca11 rollout=completed config_hash=cfg-51",
                "demo deployment ledger",
            ),
        ],
    },
    {
        "scenario_id": "timezone-history",
        "title": "Scheduled job ran at wrong local time",
        "description": "An operator says a scheduled message went out at the wrong local time.",
        "records": [
            (
                "observability",
                "log-901",
                "2026-10-19T00:30:00",
                "Schedule trigger",
                "job_id=job-91 schedule=30 0 * * * timezone=UTC customer_timezone=Asia/Kolkata",
                "demo scheduler trace",
            ),
            (
                "code_deploy",
                "code-901",
                "2026-10-18T21:00:00",
                "Schedule creation path",
                "service=scheduler revision=1c334 path=jobs/create.py function=to_cron receives timezone then stores schedule",
                "demo repository index",
            ),
            (
                "data",
                "data-901",
                "2026-10-19T00:30:01",
                "Schedule history",
                "relation=delivery_events customer_id=cust-91 schedule_timezone=UTC last_sent_at=2026-10-19T00:30:00Z",
                "demo history replica; 1 row; lag 2 seconds",
            ),
        ],
    },
    {
        "scenario_id": "search-locale",
        "title": "Search results use the wrong locale",
        "description": "A customer says product search results are not in their selected locale.",
        "records": [
            (
                "observability",
                "log-1001",
                "2026-10-19T19:10:00",
                "Search request",
                "request_id=req-1001 user_locale=fr-FR response_locale=en-US index=products-v8",
                "demo search trace",
            ),
            (
                "code_deploy",
                "code-1001",
                "2026-10-19T18:50:00",
                "Locale selection path",
                "service=search-api revision=11ea2 path=query/locales.py function=resolve_locale checks request header then account preference",
                "demo repository index",
            ),
            (
                "ai_runtime",
                "ai-1001",
                "2026-10-19T19:10:01",
                "Query rewrite run",
                "run_id=ai-1001 prompt_version=search-rewrite-v3 model=gpt-4.1-mini input_locale=fr-FR output_locale=en-US",
                "demo AI run ledger",
            ),
        ],
    },
]


async def seed_demo_data(database: Database) -> None:
    """Idempotently load demo source records. It has no conclusion/ground-truth column."""

    async with database.pool.acquire() as connection:
        async with connection.transaction():
            for scenario in DEMO_SCENARIOS:
                await connection.execute(
                    """
                    insert into incident.demo_scenarios (scenario_id, title, description)
                    values ($1, $2, $3)
                    on conflict (scenario_id) do update set title = excluded.title, description = excluded.description
                    """,
                    scenario["scenario_id"],
                    scenario["title"],
                    scenario["description"],
                )
                for kind, record_id, observed_at, summary, content, coverage in scenario["records"]:
                    await connection.execute(
                        """
                        insert into incident.demo_source_records
                          (source_record_id, scenario_id, source_kind, observed_at, summary, content, coverage_note)
                        values ($1, $2, $3, $4, $5, $6, $7)
                        on conflict (source_record_id) do update
                          set observed_at = excluded.observed_at, summary = excluded.summary,
                              content = excluded.content, coverage_note = excluded.coverage_note
                        """,
                        record_id,
                        scenario["scenario_id"],
                        kind,
                        _at(observed_at),
                        summary,
                        content,
                        coverage,
                    )
