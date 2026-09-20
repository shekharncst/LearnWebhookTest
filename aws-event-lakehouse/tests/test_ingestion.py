import json
import unittest

from event_lakehouse import ingestion


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


class TestIngestion(unittest.TestCase):
    def test_raw_key_is_partitioned_and_replay_safe(self):
        first = ingestion.raw_object_key(EVENT)
        second = ingestion.raw_object_key(dict(EVENT))

        self.assertEqual(first, second)
        self.assertTrue(
            first.startswith(
                "raw/event_type=customer_order/year=2026/month=09/day=20/hour=12/"
            )
        )

    def test_invalid_event_reports_missing_contract_field(self):
        invalid = dict(EVENT)
        del invalid["messageId"]

        with self.assertRaisesRegex(ingestion.InvalidEvent, "messageId"):
            ingestion.raw_object_key(invalid)

    def test_metric_uses_low_cardinality_event_type_dimension(self):
        metric = json.loads(ingestion.emf_metric("EventsAccepted", 1, "customer_order"))

        self.assertEqual(
            metric["_aws"]["CloudWatchMetrics"][0]["Namespace"],
            "Portfolio/EventLakehouse",
        )
        self.assertEqual(metric["EventType"], "customer_order")
        self.assertEqual(metric["EventsAccepted"], 1)
