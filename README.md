# Dential Clinic MS Agents

A microservice-based system with AI-powered agents for dental clinic management, built using FastAPI and MySQL.

---

## 🚀 Features

- General question answering agent
- Data merging from multiple sources
- Wikipedia scraping integration
- Integration with Together API for chat completions
- Secure database connection and environment variable configuration

---

## ✅ Prerequisites

- Python 3.10+
- MySQL server
- Git

---

## 🛠️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/ayoubbezai/dential-clinc-ms-agents.git
cd dential-clinc-ms-agents
```

### 2. Create and activate virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate    # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env` file

Copy the example `.env.example` or create a `.env` file with the following content:

```env
TOGETHER_API_KEY=your_together_api_key
TOGETHER_API_URL=https://api.together.xyz/v1/chat/completions

DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=dental_db
DB_USERNAME=appuser
DB_PASSWORD=your_password

GOOGLE_API_KEY=your_google_api_key

LOG_FILE=logs/agent.log
APP_ENCRYPTION_KEY_BASE64=your_encryption_key
ROLE_EXPLANATION_FILE=role_explanation.txt
```

---

## 🧩 Set up MySQL Database

Ensure:

- Your MySQL server is running
- A database named `dental_db` exists
- The user `appuser` has appropriate privileges

---

## ▶️ Running the App

```bash
python -m uvicorn app:app --reload
```

By default, the app runs at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 📂 Project Structure

```
dential-clinc-ms-agents/
│
├── app/                   # FastAPI app and routes
├── agents/                # AI agent logic
├── prompts/
├── schema_definitions/
├── tools/
├── utils/
├── logs/                  # Log files
├── .env.example           # Example environment file
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

---

## 📃 License

This project is open-source. Feel free to fork, use, and adapt it to your needs.
