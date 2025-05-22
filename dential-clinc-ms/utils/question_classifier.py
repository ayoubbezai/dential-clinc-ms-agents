# agents/classifier_agent.py

import google.generativeai as genai
from prompts.classifier_prompts import SYSTEM_PROMPT, get_classifier_prompt

def typeOfQuestion(user_question, full_schema, GEMINI_API_KEY):
    """
    Classifies the user question as DATABASE or GENERAL using Gemini.
    """
    user_prompt = get_classifier_prompt(user_question, full_schema)

    # Prepare the full prompt for Gemini
    full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"

    try:
        # Configure Gemini
        genai.configure(api_key=GEMINI_API_KEY)

        # Initialize Gemini model
        model = genai.GenerativeModel("models/gemini-1.5-flash")

        # Generate response
        response = model.generate_content(full_prompt)

        # Extract and return classification
        classification = response.text.strip()
        return classification

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return "GENERAL"  # Default fallback classification
