import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

DB_PATH = Path(os.getenv("VISUAL_AGENT_DB", Path(__file__).with_name("activity.db")))
PORT = int(os.getenv("PORT", "8787"))


def connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            page_url TEXT NOT NULL,
            page_title TEXT,
            target TEXT,
            text_value TEXT,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_events_created_at ON events(created_at DESC)"
    )
    return connection


def add_event(payload):
    required = ("sessionId", "eventType", "pageUrl")
    missing = [field for field in required if not payload.get(field)]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")
    event = {
        "id": str(uuid.uuid4()),
        "session_id": str(payload["sessionId"])[:128],
        "event_type": str(payload["eventType"])[:64],
        "page_url": str(payload["pageUrl"])[:2048],
        "page_title": str(payload.get("pageTitle", ""))[:512],
        "target": str(payload.get("target", ""))[:512],
        "text_value": str(payload.get("textValue", ""))[:1000],
        "metadata": json.dumps(payload.get("metadata", {})),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    with connect() as connection:
        connection.execute("""
            INSERT INTO events VALUES (
                :id, :session_id, :event_type, :page_url, :page_title,
                :target, :text_value, :metadata, :created_at
            )
        """, event)
    return event


def list_events(limit=100):
    if not isinstance(limit, int) or limit < 1:
        raise ValueError("limit must be a positive integer")
    with connect() as connection:
        rows = connection.execute(
            "SELECT * FROM events ORDER BY created_at DESC LIMIT ?", (min(limit, 500),)
        ).fetchall()
    return [dict(row) | {"metadata": json.loads(row["metadata"])} for row in rows]


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, body):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_json(204, {})

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            connect().close()
            return self.send_json(200, {"status": "ok", "database": str(DB_PATH)})
        if parsed.path == "/api/events":
            try:
                limit = int(parse_qs(parsed.query).get("limit", ["100"])[0])
                return self.send_json(200, {"events": list_events(limit)})
            except ValueError as error:
                return self.send_json(400, {"error": str(error)})
        self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path != "/api/events":
            return self.send_json(404, {"error": "Not found"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > 1_000_000:
                return self.send_json(413, {"error": "Payload too large"})
            payload = json.loads(self.rfile.read(length) or b"{}")
            event = add_event(payload)
            print(f"stored {event['event_type']} from {event['page_url']}")
            self.send_json(201, {"event": event})
        except (ValueError, json.JSONDecodeError) as error:
            self.send_json(400, {"error": str(error)})
        except Exception as error:
            print(f"request failed: {error}")
            self.send_json(500, {"error": "Internal server error"})

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")


if __name__ == "__main__":
    connect().close()
    print(f"Visual Agent API listening on http://localhost:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
