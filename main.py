from __future__ import annotations

import json
import mimetypes
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse, parse_qs


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
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
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

    def do_OPTIONS(self) -> None:
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        route = urlparse(self.path).path

        if route == "/api/state":
            self._send_json(read_state())
            return

        if route == "/api/users":
            self._send_json(read_state().get("users", []))
            return

        if route == "/api/messages":
            query = urlparse(self.path).query
            params = parse_qs(query)
            state = read_state()
            messages = state.get("messages", [])

            chat_with = params.get("chatWith", [None])[0]
            group_id = params.get("groupId", [None])[0]
            current_user = params.get("currentUser", [None])[0]

            if chat_with:
                my_username = current_user
                if not my_username and state.get("currentUser"):
                    my_username = state["currentUser"].get("username")
                
                filtered = [
                    msg for msg in messages
                    if msg.get("type") == "direct" and (
                        (msg.get("sender") == chat_with and msg.get("recipient") == my_username) or
                        (msg.get("sender") == my_username and msg.get("recipient") == chat_with)
                    )
                ]
                self._send_json(filtered)
                return
            elif group_id:
                filtered = [
                    msg for msg in messages
                    if msg.get("type") == "group" and msg.get("recipient") == group_id
                ]
                self._send_json(filtered)
                return
            else:
                self._send_json(messages)
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

        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8") if length else "{}"

        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON payload"}, status=400)
            return

        if route == "/api/state":
            self._send_json(write_state(payload))
            return

        elif route == "/api/users":
            username = payload.get("username", "").strip().lower()
            name = payload.get("name", "").strip()
            password = payload.get("password", "")

            if not username or not name or not password:
                self._send_json({"error": "Username, name, and password are required"}, status=400)
                return

            state = read_state()
            users = state.get("users", [])
            if any(u.get("username") == username for u in users):
                self._send_json({"error": "Username is already taken"}, status=400)
                return

            new_user = {"username": username, "name": name, "password": password}
            state["users"].append(new_user)
            write_state(state)
            self._send_json(new_user, status=201)
            return

        elif route == "/api/messages":
            sender = payload.get("sender", "").strip()
            recipient = payload.get("recipient", "").strip()
            msg_type = payload.get("type", "direct").strip()
            text = payload.get("text", "").strip()

            if not sender or not recipient or not text:
                self._send_json({"error": "Sender, recipient, and text are required"}, status=400)
                return

            import time
            import random
            state = read_state()
            new_msg = {
                "id": str(int(time.time() * 1000)) + "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=5)),
                "sender": sender,
                "type": msg_type,
                "recipient": recipient,
                "text": text,
                "timestamp": int(time.time() * 1000)
            }
            state["messages"].append(new_msg)
            write_state(state)
            self._send_json(new_msg, status=201)
            return

        elif route == "/api/groups":
            name = payload.get("name", "").strip()
            creator = payload.get("creator", "").strip()
            members = payload.get("members", [])

            if not name or not creator or not members:
                self._send_json({"error": "Group name, creator, and members are required"}, status=400)
                return

            state = read_state()
            import time
            group_id = "g_" + str(int(time.time() * 1000))
            new_group = {
                "id": group_id,
                "name": name,
                "creator": creator,
                "members": members
            }
            state["groups"].append(new_group)
            write_state(state)
            self._send_json(new_group, status=201)
            return

        self.send_error(404, "Route not found")

    def do_PUT(self) -> None:
        route = urlparse(self.path).path

        if route == "/api/messages":
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8") if length else "{}"

            try:
                payload = json.loads(body)
            except json.JSONDecodeError:
                self._send_json({"error": "Invalid JSON payload"}, status=400)
                return

            msg_id = payload.get("id")
            new_text = payload.get("text")

            if not msg_id or new_text is None:
                self._send_json({"error": "Message id and text are required"}, status=400)
                return

            state = read_state()
            messages = state.get("messages", [])
            found = False
            for msg in messages:
                if str(msg.get("id")) == str(msg_id):
                    msg["text"] = new_text
                    found = True
                    break

            if not found:
                self._send_json({"error": f"Message with id {msg_id} not found"}, status=404)
                return

            write_state(state)
            self._send_json({"success": True, "message": msg})
            return

        self.send_error(404, "Route not found")

    def do_DELETE(self) -> None:
        route = urlparse(self.path).path

        if route == "/api/messages":
            query = urlparse(self.path).query
            params = parse_qs(query)
            msg_id = params.get("id", [None])[0]

            if not msg_id:
                self._send_json({"error": "Message id parameter is required"}, status=400)
                return

            state = read_state()
            messages = state.get("messages", [])
            
            filtered_messages = [msg for msg in messages if str(msg.get("id")) != str(msg_id)]
            
            if len(filtered_messages) == len(messages):
                self._send_json({"error": f"Message with id {msg_id} not found"}, status=404)
                return

            state["messages"] = filtered_messages
            write_state(state)
            self._send_json({"success": True, "deleted_id": msg_id})
            return

        self.send_error(404, "Route not found")

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
    
    
    
    
    
    
    
    
