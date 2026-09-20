# AWS Event Lakehouse Slice

A small, reviewable reference implementation for an event-driven AWS lakehouse:

```text
EventBridge -> SQS -> Lambda -> S3 Raw -> Glue -> Bronze Parquet -> Silver Iceberg
                              \-> CloudWatch EMF metrics + DLQ/alarm
```

## Staff-engineer signals

- Explicit service boundaries and an immutable Raw contract
- Idempotent, deterministic object keys for safe replay
- Schema versioning and quarantine as first-class paths
- Layer-level service-level indicators: accepted, quarantined, failed, and processing latency
- A decision record describing tradeoffs, ownership, and the next scaling step

## Scope of the first pull request

This first slice intentionally implements only the ingestion seam:

1. Validate a synthetic `customer_order` event.
2. Build a deterministic Raw S3 key.
3. Emit CloudWatch Embedded Metric Format telemetry.
4. Unit-test the contract, replay behavior, and failure path.

The Glue Bronze/Silver implementation and CDK resources are separate follow-up pull requests so every change remains easy to review.

## Run locally

```bash
cd aws-event-lakehouse
python -m pip install -e ".[dev]"
pytest
```

No AWS account is required for the unit tests. Production deployment will use CDK TypeScript and GitHub Actions with OIDC—no stored AWS keys.

## Success criteria

| Layer | Contract | Core metric |
|---|---|---|
| Ingestion | Valid envelope, stable event ID | `EventsAccepted` |
| Raw | Immutable JSON, deterministic key | `RawWriteLatencyMs` |
| Bronze | Typed Parquet + quarantine | `BronzeRecordsWritten` |
| Silver | Canonical Iceberg table | `SilverMergeLatencyMs` |

See [the architecture decision](docs/adr-001-thin-vertical-slice.md) for tradeoffs and follow-up work.
