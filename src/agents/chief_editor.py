from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.schema import EditionStructure
from src.state import NewsletterState


system_prompt = """

Tu es le rédacteur en chef d'une newsletter tech pointue.
Ton but est de lire le catalogue d'articles bruts fournis et de construire le plan de l'édition.
RÈGLES ABSOLUES :
1. Évite toute répétition. Un même sujet ne peut pas être dans le Grand Format ET dans les Flashs.
2. Si plusieurs articles parlent du même sujet, regroupe leurs URLs dans la liste 'urls_sources' du sujet.
3. Utilise UNIQUEMENT les URLs fournies dans le catalogue.

"""

load_dotenv()
llm = ChatOpenAI(model = "gpt-4o", temperature=0)
llm_structured = llm.with_structured_output(EditionStructure)

def chief_editor_agent(state : NewsletterState):
    print("[AGENT EDITEUR EN CHEF] Début de la recherche")
    
    articles = state["articles"]

    content_listed = []
    for idx, art in enumerate(articles):
        overview = art["content"][:500].replace("\n", " ")
        content_listed += f"[{idx}] URL: {art['url']} | Titre: {art['title']} | Extrait: {overview}...\n"

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "Voici les sources disponibles cette semaine :\n{content}\n\nGénère le plan d'édition.")
    ])

    chain = prompt | llm_structured
    edition_structure = chain.invoke({"content" : content_listed})

    print("[AGENT EDITEUR EN CHEF] Plan vérouillé et assignations prêtes")

    return {"edition_structure" : edition_structure}

