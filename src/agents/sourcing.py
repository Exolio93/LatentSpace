import os
from tavily import TavilyClient
from src.state import NewsletterState
from dotenv import load_dotenv
import requests

load_dotenv()
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def get_content(url) : 
    return requests.get(f"https://r.jina.ai/{url}").text


def soursing_agent(state : NewsletterState) : 
    print("[AGENT SOURCING] Début de la recherche")

    lookback_day = state["lookback_day"]

    response = tavily_client.search(
        query = "Artificial Intelligence",
        topic = "news",
        days = lookback_day,
        max_results=5,
        search_depth="advanced",
        include_raw_content = True
        )
    
    urls = []
    articles = []

    for result in response.get("results", []) : 
        url = result["url"]
        content = get_content(url)

        urls.append(url)
        articles.append({
            "title" : result["title"],
            "url" : url,
            "date" : result.get("published_date", "Date inconnue"),
            "content" : content
        })
    print(f"[AGENT SOURCING] {len(urls)} articles récupérés !")

    return {
        "urls" : urls,
        "articles" : articles
    }
