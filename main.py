from __future__ import annotations

import json
import mimetypes
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data.json"
HOST = "127.0.0.1"
PORT = 8000

DEFAULT_STATE = {
    "users": [
        {"username": "alice", "name": "Alice Smith", "password": "123"},
        {"username": "bob", "name": "Bob Jones", "password": "123"},
        {"username": "charlie", "name": "Charlie Brown", "password": "123"},
    ],
    "messages": [
        {
            "id": "1",
            "sender": "alice",
            "type": "direct",
            "recipient": "bob",
            "text": "Hey Bob! Welcome to WhatsApp SPA.",
            "timestamp": 0,
        },
        {
            "id": "2",
            "sender": "bob",
            "type": "direct",
            "recipient": "alice",
            "text": "Thanks Alice! This is incredibly fast.",
            "timestamp": 0,
        },
    ],
    "groups": [
        {
            "id": "g1",
            "name": "Watercooler ☕",
            "creator": "alice",
            "members": ["alice", "bob", "charlie"],
        }
    ],
    "currentUser": None,
}

STATE_LOCK = threading.Lock()


def normalize_state(raw_state: object) -> dict:
    if not isinstance(raw_state, dict):
        raw_state = {}

    return {
        "users": raw_state.get("users") if isinstance(raw_state.get("users"), list) else DEFAULT_STATE["users"],
        "messages": raw_state.get("messages") if isinstance(raw_state.get("messages"), list) else DEFAULT_STATE["messages"],
        "groups": raw_state.get("groups") if isinstance(raw_state.get("groups"), list) else DEFAULT_STATE["groups"],
        "currentUser": raw_state.get("currentUser"),
    }


def ensure_data_file() -> None:
    if not DATA_FILE.exists():
        write_state(DEFAULT_STATE)


def read_state() -> dict:
    with STATE_LOCK:
        ensure_data_file()
        with DATA_FILE.open("r", encoding="utf-8") as handle:
            return normalize_state(json.load(handle))


def write_state(state: object) -> dict:
    normalized = normalize_state(state)
    with STATE_LOCK:
        with DATA_FILE.open("w", encoding="utf-8") as handle:
            json.dump(normalized, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
    return normalized


class LocalWhatsAppHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: object, status: int = 200) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def _send_file(self, file_path: Path) -> None:
        if not file_path.exists() or not file_path.is_file():
            self.send_error(404, "File not found")
            return

        content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8" if content_type.startswith("text/") or content_type == "application/javascript" else content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        route = urlparse(self.path).path

        if route == "/api/state":
            self._send_json(read_state())
            return

        if route in ("/", "/index.html"):
            self._send_file(BASE_DIR / "index.html")
            return

        if route == "/data.json":
            self._send_file(DATA_FILE)
            return

        requested = (BASE_DIR / unquote(route.lstrip("/"))).resolve()
        if BASE_DIR in requested.parents or requested == BASE_DIR:
            self._send_file(requested)
            return

        self.send_error(404, "File not found")

    def do_POST(self) -> None:
        route = urlparse(self.path).path

        if route != "/api/state":
            self.send_error(404, "File not found")
            return

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8") if length else "{}"

        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON payload"}, status=400)
            return

        self._send_json(write_state(payload))

    def log_message(self, format: str, *args) -> None:
        print(f"{self.address_string()} - {format % args}")


def main() -> None:
    ensure_data_file()
    server = ThreadingHTTPServer((HOST, PORT), LocalWhatsAppHandler)
    print(f"Serving WhatsApp SPA at http://{HOST}:{PORT}")
    print(f"JSON data file: {DATA_FILE}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
    
    
    
    
    
    
    
    
