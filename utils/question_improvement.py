# utils/question_improvement.py
import requests
from prompts.improvement_prompts import IMPROVEMENT_SYSTEM_PROMPT

def get_focused_schema(user_question, full_schema, api_url, api_key):
    """
    This agent analyzes the schema and the user question, improving the question for the SQL generator agent.
    It also tries to determine which table(s) and column(s) contain the information needed.
    """

    user_prompt = (
        f"User question: {user_question}\n"
        f"Full schema:\n{full_schema}"
    )

    messages = [
        {"role": "system", "content": IMPROVEMENT_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    payload = {
        "model": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",  
        "messages": messages,
        "temperature": 0,
        "max_tokens": 512,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=20)
        response.raise_for_status()  # Ensure the request was successful

        # Extract and return the focused schema or improved question
        focused_schema = response.json()['choices'][0]['message']['content'].strip()
        return focused_schema

    except requests.exceptions.RequestException as e:
        # Handle exceptions (network, invalid response, etc.)
        print(f"Error occurred: {str(e)}")
        return "No relevant schema found or unable to process the request."
