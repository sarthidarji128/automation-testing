# WhatsApp SPA & Practical API Testing Environment

This repository contains a premium **WhatsApp Web Clone SPA** integrated with a Python backend server (`main.py`) and a JSON-based database (`data.json`). The project is specifically designed to teach and demonstrate **Practical API Testing** using three different frameworks: **Cypress**, **Selenium**, and **Apache JMeter**.

---

## Key Features

1. **WhatsApp Web Dark Theme**: High-fidelity dark mode clone of WhatsApp Web with smooth animations and interactive message flows.
2. **RESTful CRUD Backend**: Standard REST API endpoints supporting user management, messages sending/editing/deletion, and group chats.
3. **Interactive API Inspector & Console**: A toggleable side panel inside the web interface that logs all API traffic in real-time and provides an accordion-based Manual Test Bench.
4. **12+ Automated Test Scripts**: Dedicated Cypress spec runners and Selenium automation scripts covering the six CRUD APIs.
5. **JMeter Test Plan**: A complete `.jmx` file preconfigured to test all API endpoints with a View Results Tree visualizer.

---

## 1. Quick Start (Run the Application)

### Start the Backend Server
First, activate the Python virtual environment and run the server script:
```bash
# Activate Virtual Environment (Mac/Linux)
source venv/bin/activate

# Start main.py Server
python main.py
```
The application will be served locally at:
**[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 2. API Endpoint Documentation

The Python backend (`main.py`) hosts the following RESTful API endpoints:

| Endpoint | Method | Description | Payload Example |
|---|---|---|---|
| `/api/users` | `GET` | Retrieve the directory of all registered users. | *None* |
| `/api/users` | `POST` | Sign up / Register a new test user account. | `{"username": "david", "name": "David", "password": "123"}` |
| `/api/messages` | `GET` | Fetch messages. Query params: `chatWith` or `groupId`. | *None* |
| `/api/messages` | `POST` | Send/create a new direct or group message. | `{"sender": "alice", "recipient": "bob", "type": "direct", "text": "Hi"}` |
| `/api/messages` | `PUT` | Edit/update an existing message's text. | `{"id": "17814290", "text": "Edited text"}` |
| `/api/messages` | `DELETE` | Recall/delete a message by ID. Query param: `id`. | *None* |
| `/api/groups` | `POST` | Create a new group chat room. | `{"name": "Study Group", "creator": "alice", "members": ["alice", "bob"]}` |
| `/api/state` | `GET/POST`| Fetch or write the entire JSON state (legacy support). | *Full database JSON payload* |

---

## 3. Manual Testing & Live Traffic Inspection

Open the app in your browser at `http://127.0.0.1:8000`. In the header, click the **Terminal Icon (<i class="fas fa-terminal"></i>)**:
- **API Traffic Log**: Shows a chronological list of intercepted API requests. Clicking on any request expands a syntax-highlighted visualizer showing the exact JSON Request/Response payloads.
- **Manual Test Bench**: Accordion forms allow you to manually trigger any of the API endpoints directly from the browser window and inspect the raw output.

---

## 4. Run Cypress Automated API Tests

First, install Node dependencies. If Cypress throws binary errors, download the runner:
```bash
# Install npm packages
npm install

# Force-install Cypress runner binary (if needed)
npx cypress install
```

You can execute individual Cypress tests using the Python runners:
- `python cypress_get_users.py`
- `python cypress_post_user.py`
- `python cypress_get_messages.py`
- `python cypress_post_message.py`
- `python cypress_put_message.py`
- `python cypress_delete_message.py`

*(Additionally, `python cypress_one.py` and `python cypress_two.py` remain available to run legacy suites).*

---

## 5. Run Selenium Automated API Tests

Ensure Google Chrome and Python Selenium are configured. Run any of the Python Selenium test scripts directly:
- `python selenium_get_users.py`
- `python selenium_post_user.py`
- `python selenium_get_messages.py`
- `python selenium_post_message.py`
- `python selenium_put_message.py`
- `python selenium_delete_message.py`

*(Additionally, `python selenium_one.py` and `python selenium_two.py` remain available to run legacy UI logins).*

---

## 6. JMeter Load & Performance Testing

The project contains a pre-configured JMeter test plan:
* **[View Results Tree.jmx](file:///Users/s.d./main/Personal/College/Practical-API-TESTING/View%20Results%20Tree.jmx)**

### How to use:
1. Open the Apache JMeter application GUI.
2. Select **File > Open** and locate `View Results Tree.jmx` in this directory.
3. Review the thread group containing tests for all 6 API requests.
4. Click the green "Start" button to execute the test suite.
5. Inspect request headers, bodies, response times, and payloads inside the **View Results Tree** visualizer listener.