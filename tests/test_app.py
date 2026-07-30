import os
import tempfile
import unittest

os.environ["VISUAL_AGENT_DB"] = tempfile.mktemp(suffix=".db")
from backend.app import add_event, list_events


class EventStoreTests(unittest.TestCase):
    def test_stores_and_reads_event(self):
        saved = add_event({"sessionId": "demo", "eventType": "click", "pageUrl": "https://example.com"})
        self.assertEqual(saved["event_type"], "click")
        self.assertEqual(list_events(1)[0]["id"], saved["id"])

    def test_rejects_incomplete_event(self):
        with self.assertRaises(ValueError):
            add_event({"eventType": "click"})


if __name__ == "__main__":
    unittest.main()
