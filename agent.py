import json  
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# Your APP_KEY (Laravel's APP_KEY)
app_key_base64 = "3tyULFf+K8aRX9FF6XU9XvkP18JqR35RR+MYmI1wLcU="
app_key = base64.b64decode(app_key_base64)

# The encrypted data (your example)
encoded_data = "eyJpdiI6Ii82a21LcnBROEprc3EyTHFDWFFMZHc9PSIsInZhbHVlIjoiQ2xQQWdabjhPdDR1b3ljUVBDaSs3UT09IiwibWFjIjoiMTA3NzQ4YTNmYzFhMjI4MzEzZDU1ZGE1NmQ2ZmM1ZjFiYTQ2YTFkMzhhYTJkMzUzMTI4MWRmNmNkMmQ1OGVhYiIsInRhZyI6IiJ9"

# Step 1: Decode the base64 data
decoded_data = base64.b64decode(encoded_data)

data = json.loads(base64.b64decode(encoded_data).decode('utf-8'))
print(data)

iv = base64.b64decode(data['iv'])
ciphertext = base64.b64decode(data['value'])
mac = base64.b64decode(data['mac'])


cipher = AES.new(app_key, AES.MODE_CBC, iv)

# Decrypt the ciphertext and unpad the result
decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size)

# Step 5: Output the decrypted data
print("Decrypted data:", decrypted_data.decode('utf-8'))
