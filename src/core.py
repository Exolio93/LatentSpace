from langgraph.graph import StateGraph, START, END
from agents.sourcing import soursing_agent
from state import NewsletterState

workflow = StateGraph(NewsletterState)

workflow.add_node("sourcing", soursing_agent)

workflow.add_edge(START, "sourcing")
workflow.add_edge("sourcing", END)

app = workflow.compile()

# ===================

inputs =  {
    "lookback_day" : 7,
    "urls" : [],
    "articles" : []
}

print("🚀 Lancement du pipeline...")
result = app.invoke(inputs)

print("\n--- RÉSULTATS DU SOURCING ---")
for i, article in enumerate(result["articles"][:3]): # On affiche juste les 3 premiers
    print(f"\nArticle {i+1} : {article['title']}")
    print(f"Date : {article['date']}")
    print(f"URL : {article['url']}")
    print(f"Aperçu (100 premiers caractères) : {article['content'][:100]}...")