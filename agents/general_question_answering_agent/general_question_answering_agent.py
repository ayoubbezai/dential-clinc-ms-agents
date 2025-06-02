# agents/general_question_answering_agent.py

import google.generativeai as genai
from prompts.general_question_prompt import GENERAL_QUESTION_PROMPT  # Import the prompt

def llmForGeneralQuestions(question, api_key_gemini):
    """
    This agent is responsible for handling general questions related to dental queries.
    It uses Gemini to generate a concise and informative response.

    :param question: The user's question (string)
    :param api_key_gemini: The API key for the Gemini LLM model (string)
    :return: The generated response from the Gemini LLM model (string)
    """
    try:
        # Configure the model with the provided API key
        genai.configure(api_key=api_key_gemini)
        
        # Combine the general prompt with the user's question
        prompt = GENERAL_QUESTION_PROMPT + "\nThe question to answer is: " + question

        # Set up the Gemini model and generate the response
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(prompt)

        # Return the response text from Gemini
        return response.text

    except Exception as e:
        # Handle any exceptions that occur during the process
        print(f"An error occurred: {e}")
        return None