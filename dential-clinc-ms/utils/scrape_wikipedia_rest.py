import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import quote


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
            
            return clean_text[:5000]  
        
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            continue
    
    return None





def scrape_wikipedia_rest(question: str) -> str:
    wiki_result = get_wikipedia_content(question)
    if wiki_result:
        return wiki_result


