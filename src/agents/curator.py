from dotenv import load_dotenv
from langchain_core.tools import structured
from langchain_openai import ChatOpenAI
from schema import NewsItem
import requests

load_dotenv()
llm = ChatOpenAI(model = "gpt-4o-mini")
structured_llm = llm.with_structured_output(NewsItem)

def get_content(url) : 
    return requests.get(f"https://r.jina.ai/{url}").text

def curate_article(url) : 
    raw_text = get_content(url)
    prompt = f"Analyse le texte suivant et extrais les informations clés : \n\n{raw_text}"

    result = structured_llm.invoke(prompt)
    return result

if __name__ == "__main__":
    url_a_tester = "https://www.anthropic.com/news/claude-3-5-sonnet"
    article_propre = curate_article(url_a_tester)
    
    print("\n--- RÉSULTAT STRUCTURÉ ---")
    print(f"Titre : {article_propre.title}")
    print(f"Note : {article_propre.importance}/10")
    print(f"Résumé : {article_propre.summary}")