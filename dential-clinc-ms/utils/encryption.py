import base64
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from utils.logger import log_message

# Securely load the encryption key (should be base64 in your .env)
from config import APP_ENCRYPTION_KEY_BASE64

try:
    APP_KEY = base64.b64decode(APP_ENCRYPTION_KEY_BASE64)
except Exception as e:
    log_message(f"Invalid APP_ENCRYPTION_KEY_BASE64 in config: {e}", "error")
    APP_KEY = None


def is_encrypted_data(value):
    """
    Check if the input is a base64-encoded JSON object with 'iv', 'value', and 'mac' keys.
    """
    if not isinstance(value, str):
        return False
    try:
        decoded = base64.b64decode(value)
        data = json.loads(decoded.decode("utf-8"))
        return all(k in data for k in ["iv", "value", "mac"])
    except Exception:
        return False


def decrypted_data(encoded_data):
    """
    Decrypt a base64-encoded JSON object with AES CBC encryption.
    """
    if not APP_KEY:
        return "[DECRYPTION DISABLED: Invalid APP_KEY]"

    try:
        decoded_data = base64.b64decode(encoded_data)
        data = json.loads(decoded_data.decode("utf-8"))

        iv = base64.b64decode(data["iv"])
        ciphertext = base64.b64decode(data["value"])
        mac = base64.b64decode(data["mac"])  # Placeholder if you validate MAC later

        cipher = AES.new(APP_KEY, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
        return decrypted.decode("utf-8")

    except Exception as e:
        log_message(f"Decryption error: {str(e)}", "error")
        return f"[DECRYPTION FAILED: {str(e)}]"


def decrypt_results(results):
    """
    Recursively decrypt all encrypted values in a list of dictionaries or nested dict.
    """
    if isinstance(results, list):
        return [decrypt_results(row) for row in results]
    elif isinstance(results, dict):
        return {
            key: decrypted_data(value) if is_encrypted_data(value) else value
            for key, value in results.items()
        }
    return results
