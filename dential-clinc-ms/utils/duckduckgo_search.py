import requests
from urllib.parse import quote
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def duckduckgo_search(question, retries=3, backoff_factor=0.3):
    url = f"https://api.duckduckgo.com/?q={quote(question)}&format=json&no_html=1"

    session = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # First try AbstractText
        if data.get("AbstractText"):
            return data["AbstractText"]

        # Then try RelatedTopics
        related = data.get("RelatedTopics", [])
        fallback_results = []

        def extract_texts(topics):
            for item in topics:
                if "Text" in item:
                    fallback_results.append(item["Text"])
                elif "Topics" in item:
                    extract_texts(item["Topics"])

        extract_texts(related)

        if fallback_results:
            return " • ".join(fallback_results[:3])  

        return "No information found."

    except requests.RequestException as e:
        return f"Search failed after {retries} attempts: {e}"
    except ValueError:
        return "Invalid response received from DuckDuckGo."
