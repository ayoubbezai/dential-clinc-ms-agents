# agents/sql_generation_agent.py
import requests
from prompts.sql_generation_prompt import SQL_GENERATION_PROMPT

def generate_sql(user_question, schema, api_url, api_key):
    """
    Agent to interact with an LLM to generate a SQL query based on the user question and schema.
    """

    system_prompt = SQL_GENERATION_PROMPT.format(schema=schema)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question}
    ]

    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",  # You can adjust this as needed
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
        response.raise_for_status()  # Ensure request is successful

        sql_response = response.json()['choices'][0]['message']['content'].strip()

        # Force single query output - take the first one if multiple are generated
        for line in sql_response.splitlines():
            if line.strip().startswith("SQL:"):
                return line.strip()

        return sql_response  # Fallback to full response if not in expected format

    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {str(e)}")
        return "An error occurred while generating the SQL query."
