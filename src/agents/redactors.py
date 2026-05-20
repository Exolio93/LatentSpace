from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic_core import Url
from src.schema import EditionStructure, FlashNewsList, NewsList, TopNewsItem
from src.state import NewsletterState


system_prompts = {
    "top_news" : """
    Tu es le Lead Analyst et Rédacteur Senior pour 'Latent Space', une newsletter pointue dédiée à l'IA et la Data Science.
    Ton objectif est de rédiger le 'Grand Format', l'article principal de la semaine.

    TON AUDIENCE :
    Des professionnels de la tech, des développeurs et des décideurs. Ils connaissent le milieu, tu n'as pas besoin d'expliquer ce qu'est un LLM ou un GPU. Ils veulent de l'analyse, du contexte et comprendre l'impact d'une information.

    TES RÈGLES D'OR :
    1. Respecte scrupuleusement l'angle éditorial imposé par le Rédacteur en Chef.
    2. Bannis le langage robotique et les phrases creuses (interdit d'utiliser : "Dans un monde en constante évolution", "Il est crucial de", "Naviguer dans le paysage", "En fin de compte").
    3. Va droit au but. Sois factuel, analytique, avec un ton légèrement cynique ou très pragmatique si l'actualité s'y prête.
    4. Explique toujours le "Et alors ?" (l'impact économique, stratégique ou technique).
    """,

    "news" : """
    Tu es un Chroniqueur Tech pour 'Latent Space', une newsletter IA & Data Science.
    Ton travail est de rédiger la section "Tour d'Horizon" : des actualités de taille moyenne, percutantes et très rythmées.

    TON STYLE :
    Direct, narratif et engageant. Tu racontes une histoire rapide.

    TES RÈGLES D'OR :
    1. Chaque actualité doit se lire comme une mini-histoire : le contexte rapide, le fait marquant, et la conséquence.
    2. Tu DOIS mettre en gras (avec **) 2 ou 3 termes clés par paragraphe pour rendre la lecture "scannable" pour l'œil humain.
    3. Ne donne pas ton opinion personnelle, reste factuel mais utilise une plume dynamique (vocabulaire d'action).
    4. Respecte strictement les limites de caractères de ton format. Pas de remplissage.
    """,

    "flash_news" : """
    Tu es le pupitreur "Breaking News" de la newsletter 'Latent Space'. 
    Ton objectif est de rédiger la section "Flashs", une série de brèves ultra-rapides.

    TON STYLE :
    Télégraphique, chirurgical, zéro émotion.

    TES RÈGLES D'OR :
    1. Sépare strictement l'entité (l'entreprise, la personne, le produit) du fait marquant.
    2. Le fait marquant doit tenir en UNE SEULE phrase. 
    3. Aucun commentaire, aucune analyse, aucune prise de recul. Juste l'information brute et le chiffre clé s'il y en a un.
    4. Interdiction absolue d'utiliser des mots de transition ou des fioritures.
    5. tu dois tout rédiger en francais.
    """
}



load_dotenv()

llm = ChatOpenAI(model = "gpt-4o", temperature=0)
llm_mini = ChatOpenAI(model = "gpt-4o-mini", temperature=0)


def top_news_redactor_agent(state : NewsletterState):
    print("[AGENT EDITEUR TOP NEWS] Début de la rédaction")
    
    edition_structure = state["edition_structure"]
    topic = edition_structure.top_news_subject

    correction_warning = ""
    report = state.get("quality_report")
    if report and report.revise_top_news and report.feedback_top_news:
        correction_warning = f"URGENT - TON PRÉCÉDENT BROUILLON A ÉTÉ REFUSÉ. CORRIGE CECI : {report.feedback_top_news}\n\n"

    content = ""
    for art in state.get("articles", []) :
        if art["url"] in topic.urls_sources : 
            content += f"### SOURCE : {art['title']}\n"
            content += f"URL: {art['url']}\n"
            content += f"{art['content']}\n\n"

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompts["top_news"]),
        ("user", "{correction} SUJET ASSIGNÉ : {titre}. ANGLE ÉDITORIAL IMPOSÉ : {angle}. Voici les sources brutes extraites du web pour \
            t'aider à rédiger : {sources}. Génère l'objet structuré pour le Grand Format en respectant parfaitement ces consignes.")
    ])

    chain = prompt | llm.with_structured_output(TopNewsItem)
    top_news_item = chain.invoke({
        "correction" : correction_warning,
        "titre": topic.title,
        "angle": topic.editorial_perspective,
        "sources": content
    })

    print("[AGENT EDITEUR TOP NEWS] Rédaction faite.")
    return {"top_news_item" : top_news_item}



def news_redactor_agent(state: NewsletterState):
    print("[AGENT EDITEUR NEWS] Début de la rédaction")
    
    edition_structure = state["edition_structure"]
    topics = edition_structure.news_subject 

    correction_warning = ""
    report = state.get("quality_report")
    if report and report.revise_news and report.feedback_news:
        correction_warning = f"URGENT - TON PRÉCÉDENT BROUILLON A ÉTÉ REFUSÉ. CORRIGE CECI : {report.feedback_news}\n\n"

    content = ""
    for idx, topic in enumerate(topics, 1):
        content += f"=== ACTUALITÉ {idx} ===\n"
        content += f"SUJET ASSIGNÉ : {topic.title}\n"
        content += f"ANGLE ÉDITORIAL IMPOSÉ : {topic.editorial_perspective}\n"
        content += "SOURCES BRUTES :\n"
        
        for art in state.get("articles", []):
            if art["url"] in topic.urls_sources: 
                content += f"### SOURCE : {art['title']}\n"
                content += f"URL: {art['url']}\n"
                content += f"{art['content']}\n\n"
                
        content += "-" * 50 + "\n\n"

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompts["news"]),
        ("user", "{correction} Voici les {nombre_sujets} actualités à traiter avec leurs angles et sources respectives :\n\n{sources}\n\n\
            Génère l'objet structuré contenant ces actualités en respectant parfaitement les consignes.")
    ])

    chain = prompt | llm_mini.with_structured_output(NewsList)
    
    news_list = chain.invoke({
        "correction" : correction_warning,
        "nombre_sujets": len(topics),
        "sources": content
    })

    print("[AGENT EDITEUR NEWS] Rédaction faite.")
    return {"news_list": news_list}


def flash_news_redactor_agent(state: NewsletterState):
    print("[AGENT EDITEUR FLASH NEWS] Début de la rédaction")
    
    edition_structure = state["edition_structure"]
    topics = edition_structure.flash_news_subject 

    correction_warning = ""
    report = state.get("quality_report")
    if report and report.revise_flash_news and report.feedback_flash_news:
        correction_warning = f"URGENT - TON PRÉCÉDENT BROUILLON A ÉTÉ REFUSÉ. CORRIGE CECI : {report.feedback_flash_news}\n\n"

    content = ""
    for idx, topic in enumerate(topics, 1):
        content += f"=== FLASH {idx} ===\n"
        content += f"SUJET ASSIGNÉ : {topic.title}\n"
        content += f"ANGLE ÉDITORIAL IMPOSÉ : {topic.editorial_perspective}\n"
        content += "SOURCES BRUTES :\n"
        
        for art in state.get("articles", []):
            if art["url"] in topic.urls_sources: 
                content += f"### SOURCE : {art['title']}\n"
                content += f"URL: {art['url']}\n"
                content += f"{art['content']}\n\n"
                
        content += "-" * 50 + "\n\n"

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompts["flash_news"]),
        ("user", "{correction} Voici les {nombre_sujets} actualités brèves à traiter avec leurs sources respectives :\n\n{sources}\n\n\
            Génère l'objet structuré contenant ces flashs en respectant parfaitement les consignes de concision extrême.")
    ])

    chain = prompt | llm_mini.with_structured_output(FlashNewsList)
    
    flash_news_list = chain.invoke({
        "correction" : correction_warning,
        "nombre_sujets": len(topics),
        "sources": content
    })

    print("[AGENT EDITEUR FLASH NEWS] Rédaction faite.")
    return {"flash_news_list": flash_news_list}