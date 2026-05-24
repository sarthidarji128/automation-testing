from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data.json"
APP_URL = "http://127.0.0.1:8000/#/signup"

SIGNUP_NAME = "Test User"
SIGNUP_USERNAME = "testuser_automation_01"
SIGNUP_PASSWORD = "123456"


def load_state() -> dict:
    with DATA_FILE.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_state(state: dict) -> None:
    with DATA_FILE.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def reset_current_user() -> None:
    state = load_state()
    state["currentUser"] = None
    save_state(state)


def wait_for_server(url: str, timeout_seconds: int = 10) -> None:
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

    raise SystemExit(f"The local server is not reachable at {url}. Start main.py first. Last error: {last_error}")


def main() -> None:
    wait_for_server("http://127.0.0.1:8000/")
    reset_current_user()

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 15)

    try:
        driver.get(APP_URL)
        time.sleep(2)

        name_input = wait.until(EC.visibility_of_element_located((By.ID, "signup-name")))
        username_input = wait.until(EC.visibility_of_element_located((By.ID, "signup-username")))
        password_input = wait.until(EC.visibility_of_element_located((By.ID, "signup-password")))

        name_input.clear()
        name_input.send_keys(SIGNUP_NAME)
        time.sleep(2)

        username_input.clear()
        username_input.send_keys(SIGNUP_USERNAME)
        time.sleep(2)

        password_input.clear()
        password_input.send_keys(SIGNUP_PASSWORD)
        time.sleep(2)

        signup_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#signup-form .auth-btn")))
        signup_button.click()

        time.sleep(5)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
