import os
from config import SCHEMA_PATH
from utils.logger import log_message

def load_schema():
    """
    Load SQL schema from the path defined in SCHEMA_PATH.

    Returns:
        str: Contents of the schema file, or None if loading fails.
    """
    if not os.path.exists(SCHEMA_PATH):
        log_message(f"Schema file not found at: {SCHEMA_PATH}", "error")
        return None

    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        log_message(f"Failed to load schema from {SCHEMA_PATH}: {e}", "error")
        return None
