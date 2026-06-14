from __future__ import annotations

import json
import sys
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
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 15)

    try:
        driver.get(APP_URL)
        time.sleep(1)

        unique_id = str(int(time.time()))[-6:]
        signup_username = f"user_{unique_id}"
        signup_name = f"Selenium User {unique_id}"

        # Signup form
        name_input = wait.until(EC.visibility_of_element_located((By.ID, "signup-name")))
        username_input = wait.until(EC.visibility_of_element_located((By.ID, "signup-username")))
        password_input = wait.until(EC.visibility_of_element_located((By.ID, "signup-password")))

        name_input.clear()
        name_input.send_keys(signup_name)
        username_input.clear()
        username_input.send_keys(signup_username)
        password_input.clear()
        password_input.send_keys("123")

        signup_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#signup-form .auth-btn")))
        signup_button.click()

        # Wait for chat page
        wait.until(EC.url_contains("#/chat"))
        
        # Verify db has user
        state = load_state()
        users = state.get("users", [])
        created_user = next((u for u in users if u.get("username") == signup_username), None)
        assert created_user is not None, "User should be present in database state after signup"
        print("POST User API via Selenium passed successfully.")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
