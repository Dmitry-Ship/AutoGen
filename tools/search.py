from typing_extensions import Annotated
from dotenv import load_dotenv
from tavily import TavilyClient
import os

load_dotenv()
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def search_internet(query: Annotated[str, "The query to search for"]) -> Annotated[str, "The answer to the query"]:
    print("🔍 searching ...")
    response = tavily.search(query=query, search_depth="advanced", include_images=True, include_answer=True)
    context = [{"url": obj["url"], "content": obj["content"]} for obj in response['results']]

    return context


    

