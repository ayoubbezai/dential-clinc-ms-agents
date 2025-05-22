# agents/improvement_agent.py

import google.generativeai as genai
from prompts.improvement_prompts import IMPROVEMENT_SYSTEM_PROMPT

def get_focused_schema(user_question, full_schema, GEMINI_API_KEY):
    """
    Uses Gemini to analyze the user question and schema, improving the question and identifying relevant tables/columns.
    """

    # Combine prompt and schema
    full_prompt = (
        f"{IMPROVEMENT_SYSTEM_PROMPT}\n\n"
        f"User question: {user_question}\n"
        f"Full schema:\n{full_schema}"
    )

    try:
        # Configure Gemini with API key
        genai.configure(api_key=GEMINI_API_KEY)

        # Initialize the model
        model = genai.GenerativeModel("models/gemini-1.5-flash")

        # Generate the response
        response = model.generate_content(full_prompt)

        # Return cleaned-up output
        focused_schema = response.text.strip()
        return focused_schema

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return "No relevant schema found or unable to process the request."
