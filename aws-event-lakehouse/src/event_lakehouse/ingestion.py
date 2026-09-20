"""Pure ingestion logic kept separate from AWS adapters for fast tests."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any

REQUIRED_FIELDS = {
    "eventType",
    "payloadType",
    "messageId",
    "eventTime",
    "businessKey",
    "op",
    "schemaVersion",
    "payload",
}


class InvalidEvent(ValueError):
    """Raised when an event violates the public ingestion contract."""


def validate_event(event: dict[str, Any]) -> None:
    missing = sorted(REQUIRED_FIELDS - event.keys())
    if missing:
        raise InvalidEvent(f"missing required fields: {', '.join(missing)}")
    if event["payloadType"] not in {"INLINE", "S3_REF"}:
        raise InvalidEvent("payloadType must be INLINE or S3_REF")
    if event["op"] not in {"I", "U", "D"}:
        raise InvalidEvent("op must be I, U, or D")
    try:
        datetime.fromisoformat(str(event["eventTime"]))
    except ValueError as exc:
        raise InvalidEvent("eventTime must be ISO-8601") from exc


def raw_object_key(event: dict[str, Any]) -> str:
    """Return a stable key: replaying the same event targets the same object."""
    validate_event(event)
    occurred = datetime.fromisoformat(str(event["eventTime"]))
    digest_input = f'{event["eventType"]}#{event["businessKey"]}#{event["messageId"]}'
    event_id = hashlib.sha256(digest_input.encode()).hexdigest()[:20]
    return (
        f'raw/event_type={event["eventType"]}/'
        f"year={occurred:%Y}/month={occurred:%m}/day={occurred:%d}/hour={occurred:%H}/"
        f"{event_id}.json"
    )


def canonical_json(event: dict[str, Any]) -> bytes:
    validate_event(event)
    return json.dumps(event, sort_keys=True, separators=(",", ":")).encode()


def emf_metric(name: str, value: float, event_type: str) -> str:
    """Create one CloudWatch Embedded Metric Format log entry."""
    now_ms = int(datetime.now(UTC).timestamp() * 1000)
    body = {
        "_aws": {
            "Timestamp": now_ms,
            "CloudWatchMetrics": [{
                "Namespace": "Portfolio/EventLakehouse",
                "Dimensions": [["EventType"]],
                "Metrics": [{"Name": name, "Unit": "Count"}],
            }],
        },
        "EventType": event_type,
        name: value,
    }
    return json.dumps(body, separators=(",", ":"))
