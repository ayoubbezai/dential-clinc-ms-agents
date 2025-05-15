import google.generativeai as genai

WIKIPEDIA_QUERY_OPTIMIZER_PROMPT = """
You are a query optimization agent. Your job is to take a natural language question and convert it into a concise, Wikipedia-searchable topic or phrase.

Guidelines:
- Output only 1 phrase or keyword per question
- Avoid verbs and full sentences
- Avoid vague or overly broad queries
- Prefer proper nouns or specific terms if possible
- Remove question words like "why", "how", "what","?"
- Do not explain or add anything else
- Do not add any additional information or context
- Do not use any special characters or punctuation
- must be lowercase all of them

Examples:
Input: "What causes tooth decay?"
Output: "tooth_decay"

Input: "Tell me about bleeding gums"
Output: "gingivitis"

Input: "How to prevent cavities?"
Output: "dental_caries_prevention"

Now convert this question: "{question}"
"""

def generate_wikipedia_query(question, api_key_gemini):
    """
    Reformats a natural question into a concise, Wikipedia-searchable phrase.

    :param question: The user's original question
    :param api_key_gemini: Gemini API key
    :return: A concise search term suitable for Wikipedia
    """
    try:
        genai.configure(api_key=api_key_gemini)

        prompt = WIKIPEDIA_QUERY_OPTIMIZER_PROMPT.format(question=question)
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(prompt)

        return response.text.strip()
    except Exception as e:
        print(f"[Wikipedia Query Agent Error]: {e}")
        return ""
