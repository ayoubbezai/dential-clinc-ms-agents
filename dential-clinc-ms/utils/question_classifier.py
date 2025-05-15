import requests
from prompts.classifier_prompts import SYSTEM_PROMPT, get_classifier_prompt

def typeOfQuestion(user_question, full_schema, api_url, api_key):
    """
    Classifies the user question as DATABASE or GENERAL based on its content and schema.
    """
    user_prompt = get_classifier_prompt(user_question, full_schema)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    payload = {
        "model":"mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": messages,
        "temperature": 0,
        "max_tokens": 20,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()  # Ensure the request was successful

        # Extract and return classification result
        classification = response.json()['choices'][0]['message']['content'].strip()
        return classification
    
    except requests.exceptions.RequestException as e:
        # Handle exceptions (network, invalid response, etc.)
        print(f"Error occurred: {str(e)}")
        return "GENERAL"  # Default classification in case of an error
