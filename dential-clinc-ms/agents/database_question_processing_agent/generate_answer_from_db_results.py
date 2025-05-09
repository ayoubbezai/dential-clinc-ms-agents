# agents/generate_answer_from_db_results.py

import requests
from prompts.answer_generation_prompt import ANSWER_GENERATION_SYSTEM_PROMPT  # Import the prompt

def generate_answer_from_db_results(clean_sql,user_question, db_results, api_url, api_key):
    """
    Given the user's question and the database results, generate a clear, concise answer using the LLM.

    :param user_question: The original question from the user (str)
    :param db_results: The results from the executed SQL query (could be a list or dict)
    :param api_url: The API endpoint URL for the LLM (str)
    :param api_key: The API key to authenticate the request (str)
    :return: The generated answer based on the user question and the database results (str)
    """

    # Format the user prompt with the actual user question and database results
    user_prompt = (
        f"this the sql generated :{clean_sql}"
        f"User question: {user_question}\n"
        f"Database results: {db_results}"
    )

    # Combine system prompt and user prompt in the messages list for the LLM
    messages = [
        {"role": "system", "content": ANSWER_GENERATION_SYSTEM_PROMPT},  # Use the imported system prompt
        {"role": "user", "content": user_prompt}
    ]

    # Prepare the payload for the API request
    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",  # Use the appropriate model as per your requirement
        "messages": messages,
        "temperature": 0,  # Ensures more deterministic output
        "max_tokens": 512,  # You can adjust max tokens to suit the expected answer length
    }

    # Set the headers for the request (using API key for authentication)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        # Send the request to the LLM API
        response = requests.post(api_url, headers=headers, json=payload, timeout=20)
        
        # Ensure the request was successful
        response.raise_for_status()
        
        # Extract the answer from the response
        answer = response.json()['choices'][0]['message']['content'].strip()
        
        return answer
    except requests.exceptions.RequestException as e:
        # Handle request errors (e.g., network issues, invalid API keys)
        print(f"Error with the LLM API request: {str(e)}")
        return "An error occurred while fetching the answer."
