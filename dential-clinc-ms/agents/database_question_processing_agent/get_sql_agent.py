# agents/sql_generation_agent.py
import requests
from prompts.sql_generation_prompt import SQL_GENERATION_PROMPT
import google.generativeai as genai


def generate_sql(user_question, schema,GEMINI_API_KEY):
    """
    Agent to interact with an LLM to generate a SQL query based on the user question and schema.
    """

    system_prompt = SQL_GENERATION_PROMPT.format(schema=schema)

  

    try:
               # Configure the model with the provided API key
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Combine the general prompt with the user's question
        prompt = system_prompt + "\nThe question to answer is: " + user_question

        # Set up the Gemini model and generate the response
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(prompt)

        # Return the response text from Gemini
        return response.text

    except response.exceptions.RequestException as e:
        print(f"Error occurred: {str(e)}")
        return "An error occurred while generating the SQL query."
