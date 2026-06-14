from __future__ import annotations

import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
APP_URL = "http://127.0.0.1:8000/"
SERVER_SCRIPT = BASE_DIR / "main.py"
TEST_SPEC = "cypress/e2e/post_message.cy.js"


def wait_for_server(url: str, timeout_seconds: int = 15) -> None:
    deadline = time.time() + timeout_seconds
    last_error: Exception | None = None

    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as error:
            last_error = error
            time.sleep(0.5)

    raise SystemExit(f"The local server is not reachable at {url}. Start main.py first or let this script launch it. Last error: {last_error}")


def ensure_server_running() -> subprocess.Popen[bytes] | None:
    try:
        with urllib.request.urlopen(APP_URL, timeout=2) as response:
            if response.status == 200:
                return None
    except Exception:
        pass

    return subprocess.Popen([sys.executable, str(SERVER_SCRIPT)], cwd=BASE_DIR)


def run_cypress() -> int:
    command = [
        "npx",
        "cypress",
        "run",
        "--spec",
        TEST_SPEC,
        "--config",
        "video=true,trashAssetsBeforeRuns=false",
    ]
    completed = subprocess.run(command, cwd=BASE_DIR)
    return completed.returncode


def main() -> None:
    server_process = ensure_server_running()
    try:
        wait_for_server(APP_URL)
        exit_code = run_cypress()
        raise SystemExit(exit_code)
    finally:
        if server_process is not None:
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()


if __name__ == "__main__":
    main()
