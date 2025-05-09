import os
import datetime

# Load log path from environment or set default
LOG_FILE = os.getenv("LOG_FILE", "logs/agent.log")

# Ensure log directory exists
log_dir = os.path.dirname(LOG_FILE)
if log_dir:  # Only make dirs if a directory path exists
    os.makedirs(log_dir, exist_ok=True)

def log_message(message, level="info"):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{now}] [{level.upper()}] {message}\n"

    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(formatted)
