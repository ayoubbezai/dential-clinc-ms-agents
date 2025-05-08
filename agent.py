import os
import requests
from dotenv import load_dotenv
from datetime import datetime

# Configure logging
def log_message(message, level="info"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {level.upper()}: {message}"
    print(log_entry)
    # Ensure the log file is written with UTF-8 encoding
    with open("dental_assistant.log", "a", encoding='utf-8') as log_file:
        log_file.write(log_entry + "\n")

# Load configuration
def load_config():
    load_dotenv()
    config = {
        "api_key": os.getenv("TOGETHER_API_KEY"),
        "api_url": os.getenv("TOGETHER_API_URL"),
        "role_file": os.getenv("ROLE_EXPLANATION_FILE")
    }
    
    if not all([config["api_key"], config["api_url"], config["role_file"]]):
        raise ValueError("Missing required environment variables")
    return config

# Load role description
def load_role_description(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        log_message(f"Error loading role: {str(e)}", "error")
        raise

# Get AI response
def get_ai_response(prompt, api_url, api_key, max_tokens=500):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": prompt,
        "temperature": 0.5,
        "max_tokens": max_tokens,
        "top_p": 0.85,
        "frequency_penalty": 0.2,
        "presence_penalty": 0.2
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        log_message(f"API error: {str(e)}", "error")
        return None

# Generate response
def generate_response(question, context, api_url, api_key):
    system_prompt = {
        "role": "system",
        "content": f"{context}\nIMPORTANT: Keep responses extremely concise (1-2 sentences maximum)."
    }
    
    user_prompt = {
        "role": "user",
        "content": f"Question: {question}\nProvide a very brief, direct response:"
    }
    
    response = get_ai_response([system_prompt, user_prompt], api_url, api_key)
    if not response:
        return "Unable to generate response. Please try again."
    
    return response.strip()

def main():
    try:
        config = load_config()
        context = load_role_description(config["role_file"])
        
        print("\nDental Assistant")
        print("Type your question or 'exit' to quit\n")
        
        while True:
            question = input("Question: ").strip()
            if question.lower() in ["exit", "quit"]:
                print("Goodbye.")
                break
                
            if not question:
                continue
                
            response = generate_response(
                question, 
                context, 
                config["api_url"], 
                config["api_key"]
            )
            
            print("\n" + "-"*50)
            print(response)
            print("-"*50 + "\n")
            
    except Exception as e:
        log_message(f"System error: {str(e)}", "critical")
        print("System error occurred. Check logs for details.")

if __name__ == "__main__":
    main()
