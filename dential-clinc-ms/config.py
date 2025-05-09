import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# === API KEYS ===
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_API_URL = os.getenv("TOGETHER_API_URL")

# === MODEL SETTINGS ===
GEMINI_MODEL = "models/gemini-1.5-flash"
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 1024))

# === DB CONFIG ===
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME", "dential-clinic-ms")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# === PATHS ===
SCHEMA_PATH = "schema_definitions/schema.sql"
APP_ENCRYPTION_KEY_BASE64 = os.getenv("APP_ENCRYPTION_KEY_BASE64")