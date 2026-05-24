# Running the Local WhatsApp SPA

This project uses a local Python server and a JSON file for persistence. Start the server first, then run either Selenium automation script in a separate terminal.

## 1. Start the app server

From the project folder, run:

```bash
python main.py
```

If you are using the virtual environment in this workspace, activate it first:

```bash
source venv/bin/activate
```

The server will open the app at:

```text
http://127.0.0.1:8000
```

The app reads and writes state in `data.json`.

## 2. Run the login automation

In a second terminal, run:

```bash
python selenium_one.py
```

What it does:

1. Opens the browser on the local WhatsApp SPA.
2. Waits for the login page to load.
3. Types the username and password.
4. Clicks the Login button.
5. Waits 5 seconds and closes the browser.

You can also pass credentials on the command line:

```bash
python selenium_one.py your_username your_password
```

## 3. Run the signup automation

In a second terminal, run:

```bash
python selenium_two.py
```

What it does:

1. Opens the browser on the signup page.
2. Waits for the signup form to load.
3. Enters the hard-coded signup name, username, and password.
4. Clicks the Sign Up button.
5. Waits 5 seconds and closes the browser.

The hard-coded values are defined near the top of `selenium_two.py`.

## 4. Run the Cypress automation

Install the npm dependency first:

```bash
npm install
```

Then run the Cypress test launcher:

```bash
python cypress_one.py
```

What it does:

1. Starts `main.py` if the local server is not already running.
2. Opens the app in Cypress.
3. Logs in as a local user.
4. Opens another user chat and sends a message.
5. Verifies the message is stored in `data.json`.
6. Stops the server it started.

## Notes

- Keep `main.py` running while you use the Selenium scripts.
- If the browser does not open, make sure Google Chrome is installed.
- The automation scripts update `data.json`, so any signups, logins, chats, or group messages are stored locally in that file.