import google.generativeai as genai
from prompts.answer_generation_prompt import ANSWER_GENERATION_SYSTEM_PROMPT
from utils.masking import mask_db_results_keys_only, mask_db_results_values


def generate_answer_from_db_results(clean_sql, user_question, db_results, GEMINI_API_KEY, mask_mode="keys"):
    """
    Uses Gemini to generate an answer, masking DB results to protect sensitive data.
    Replaces masked placeholders with actual values after generation.
    """

    # Generate placeholder-masked version
    placeholder_masked_result = {}
    if db_results and isinstance(db_results, list):
        row = db_results[0]
        placeholder_masked_result = {
            key: f"[value of {key} from the database results]" for key in row
        }

    # Select masking strategy for prompt (structure only, or keys only)
    if mask_mode == "keys":
        masked_db_results = mask_db_results_keys_only(db_results)
    elif mask_mode == "values":
        masked_db_results = placeholder_masked_result  # Inject placeholders
    else:
        raise ValueError("Invalid mask_mode. Choose 'keys' or 'values'.")

    # Compose prompt
    print("what is send to llm",masked_db_results)
    full_prompt = (
        f"{ANSWER_GENERATION_SYSTEM_PROMPT}\n\n"
        f"This is the SQL generated: {clean_sql}\n"
        f"User question: {user_question}\n"
        f"Database results (masked): {masked_db_results}"
    )

    try:
        # Call Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(full_prompt)
        raw_answer = response.text.strip()

        # Replace placeholders with real values
        final_answer = replace_placeholders(raw_answer, db_results)
        return final_answer

    except Exception as e:
        print(f"Error with the Gemini API: {str(e)}")
        return "An error occurred while fetching the answer."


def replace_placeholders(answer, db_results):
    """
    Replaces LLM-safe placeholders in the answer with actual DB values.
    """
    if not db_results or not isinstance(db_results, list):
        return answer

    row = db_results[0]
    for key, value in row.items():
        placeholder = f"[value of {key} from the database results]"
        answer = answer.replace(placeholder, str(value))

    return answer
