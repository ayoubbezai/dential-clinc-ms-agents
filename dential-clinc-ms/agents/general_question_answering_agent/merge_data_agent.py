import google.generativeai as genai
from utils.scrape_wikipedia_rest import scrape_wikipedia_rest
from utils.duckduckgo_search import duckduckgo_search
from prompts.scraped_data_to_answer import   PROMPT_SCRAPED_DATA_TO_ANSWER

def merge_scraped_data(question,GEMINI_API_KEY):
    """
    Merge Wikipedia and DuckDuckGo data, and generate a concise answer using Gemini.
    """
    try:
        # Step 1: Scrape external sources
        wikipedia_answer = scrape_wikipedia_rest(question)
        duckduckgo_answer = duckduckgo_search(question) if not wikipedia_answer else None

        # Step 2: Combine available content
        combined_info = ""
        if wikipedia_answer:
            combined_info += f"Wikipedia says:\n{wikipedia_answer}\n\n"
        if duckduckgo_answer:
            combined_info += f"DuckDuckGo found:\n{duckduckgo_answer}"

        if not combined_info.strip():
            return {
                "answer": "No relevant information found from Wikipedia or DuckDuckGo.",
                "wikipedia_answer": wikipedia_answer,
                "duckduckgo_answer": duckduckgo_answer
            }

        # Step 3: Generate final answer using Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        prompt = (
            "{PROMPT_SCRAPED_DATA_TO_ANSWER} "
            f"Question:{question}"
            f"combined_info:{combined_info}"

        )

        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(prompt)

        return {
            "answer": response.text,
            "wikipedia_answer": wikipedia_answer,
            "duckduckgo_answer": duckduckgo_answer
        }

    except Exception as e:
        print(f"Error occurred: {e}")
        return {
            "error": True,
            "message": str(e)
        }
