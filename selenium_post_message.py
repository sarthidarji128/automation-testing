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
APP_URL = "http://127.0.0.1:8000/#/login"


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

        # Login
        username_input = wait.until(EC.visibility_of_element_located((By.ID, "login-username")))
        password_input = wait.until(EC.visibility_of_element_located((By.ID, "login-password")))

        username_input.clear()
        username_input.send_keys("alice")
        password_input.clear()
        password_input.send_keys("123")

        login_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#login-form .auth-btn")))
        login_button.click()

        # Wait for chat page
        wait.until(EC.url_contains("#/chat"))

        # Click tab "All Users"
        users_tab = wait.until(EC.element_to_be_clickable((By.ID, "tab-users")))
        users_tab.click()
        time.sleep(1)

        # Select Bob
        bob_item = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'item-name') and text()='Bob Jones']")))
        bob_item.click()
        time.sleep(1)

        # Write and send message
        unique_message = f"Hello Bob! Automated Selenium msg {int(time.time())}"
        message_input = wait.until(EC.visibility_of_element_located((By.ID, "message-input")))
        message_input.clear()
        message_input.send_keys(unique_message)
        
        send_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".message-input-bar i[title='Send']")))
        send_btn.click()
        time.sleep(2)

        # Verify chat list has the message
        chat_history = wait.until(EC.visibility_of_element_located((By.ID, "message-list"))).text
        assert unique_message in chat_history, "Sent message should be visible in chat area"
        print("POST Message API via Selenium passed successfully.")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
