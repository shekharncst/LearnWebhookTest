# ADR-001: Start with a thin ingestion-to-Raw slice

- Status: Accepted
- Date: 2026-09-20

## Context

The target architecture is Kafka/MM2/MSK to immutable Raw, then controlled Raw-to-Bronze-to-Silver processing. A portfolio implementation must demonstrate the same engineering judgment without creating an expensive always-on MSK environment or one oversized pull request.

## Decision

The first slice uses EventBridge, SQS, Lambda, and S3 Raw. Event envelopes use synthetic customer-order data. Raw keys are deterministic, so SQS redelivery and explicit replay do not create duplicate logical objects.

The public boundary is Raw. A later Glue job owns Raw-to-Bronze conversion; a separate job owns canonical Silver Iceberg merge behavior. Invalid contracts go to quarantine and delivery failures go to a DLQ. CloudWatch EMF records accepted, quarantined, failed, and latency signals.

## Consequences

- The implementation is inexpensive and locally testable.
- It preserves the production boundary and replay model.
- It does not claim Lambda is the production Kafka consumer.
- MSK/MM2 is documented as the scale-out transport, not required for this learning slice.

## Review sequence

1. Ingestion contract, deterministic keys, tests, and EMF metrics.
2. CDK TypeScript for EventBridge, SQS/DLQ, Lambda, encrypted S3, and alarms.
3. Glue Raw-to-Bronze Parquet with quarantine and data-quality metrics.
4. Glue Bronze-to-Silver Iceberg merge with checkpoint/replay tests.
5. GitHub Actions OIDC deployment and an operational runbook.

## Staff-level discussion prompts

- Which team owns the Raw contract and schema compatibility policy?
- What replay rate protects downstream SLAs during recovery?
- Which metrics are SLIs, and what error budget triggers an operational review?
- When does the serverless transport become less suitable than MSK/MM2?
