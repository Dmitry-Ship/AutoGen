from duckduckgo_search import DDGS
from typing import Optional
import requests
from bs4 import BeautifulSoup

def search_internet(query: str, max_results: int =1) -> list[str]:
    with DDGS() as ddgs:
        return [r for r in ddgs.text(query, max_results=max_results)]
    
def fetch_website(url: str) -> Optional[str]:
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        # Check for successful access to the webpage
        if response.status_code == 200:
            # Parse the HTML content of the page using BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            # Extract the content of the <body> tag
            body_content = soup.find("body")
            # Return all the text in the body tag, stripping leading/trailing whitespaces
            return " ".join(body_content.stripped_strings) if body_content else None
        else:
            # Return None if the status code isn't 200 (success)
            return None
    except requests.RequestException:
        # Return None if any request-related exception is caught
        return None