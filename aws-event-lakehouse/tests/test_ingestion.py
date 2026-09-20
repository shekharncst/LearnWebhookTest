import json

import pytest

from event_lakehouse.ingestion import emf_metric, InvalidEvent, raw_object_key


EVENT = {
    "eventType": "customer_order",
    "payloadType": "INLINE",
    "messageId": "msg-0001",
    "eventTime": "2026-09-20T12:00:00Z",
    "businessKey": "order-1001",
    "op": "I",
    "schemaVersion": "1.0",
    "payload": {"amount": 74.25},
}


def test_raw_key_is_partitioned_and_replay_safe():
    first = raw_object_key(EVENT)
    second = raw_object_key(dict(EVENT))

    assert first == second
    assert first.startswith(
        "raw/event_type=customer_order/year=2026/month=09/day=20/hour=12/"
    )


def test_invalid_event_reports_missing_contract_field():
    invalid = dict(EVENT)
    del invalid["messageId"]

    with pytest.raises(InvalidEvent, match="messageId"):
        raw_object_key(invalid)


def test_metric_uses_low_cardinality_event_type_dimension():
    metric = json.loads(emf_metric("EventsAccepted", 1, "customer_order"))

    assert metric["_aws"]["CloudWatchMetrics"][0]["Namespace"] == "Portfolio/EventLakehouse"
    assert metric["EventType"] == "customer_order"
    assert metric["EventsAccepted"] == 1
