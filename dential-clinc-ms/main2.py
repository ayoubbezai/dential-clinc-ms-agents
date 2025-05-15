import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import quote

# ====================== 1. Wikipedia Direct Scraper ======================
def get_wikipedia_content(question, max_retries=3):
    base_url = "https://en.wikipedia.org/wiki/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for attempt in range(max_retries):
        try:
            # Encode question for URL
            encoded_question = quote(question.replace(' ', '_'))
            url = f"{base_url}{encoded_question}"
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get the main content
            content = soup.find(id="mw-content-text")
            if not content:
                return None
                
            # Clean up the text
            paragraphs = content.find_all('p')
            clean_text = '\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
            return clean_text[:5000]  # Return first 5000 characters
        
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            continue
    
    return None



# ====================== 3. Main Research Function ======================
def research_question(question):
    print(f"\n🔍 Researching: '{question}'")
    
    # Try Wikipedia first
    print("\n=== Trying Wikipedia ===")
    wiki_result = get_wikipedia_content(question)
    
    if wiki_result:
        print(wiki_result)
        return wiki_result
    


# ====================== Example Usage ======================
if __name__ == "__main__":
    while True:
        question = input("\nEnter your question (or 'quit' to exit): ")
        if question.lower() == 'quit':
            break
        research_question(question)