from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from schema import QualityReport
from state import NewsletterState
from langchain_openai import ChatOpenAI

system_prompt = """
Tu es le Secrétaire de Rédaction intransigeant de Latent Space.
Analyse les articles générés par tes rédacteurs.

TES CRITÈRES :
1. Aucune répétition d'information entre le 'Top News', les 'News' et les 'Flashs'.
2. Le ton ne doit pas être robotique.
3. Le format de chaque section doit être respecté.

Mets le booléen d'une section à 'True' uniquement si elle nécessite une réécriture.
Ne te sens pas obligé de retourner forcément obligé de signaler des corrections si c'est déjà bien fait, car cela coûte des tokens. 
Si tout est bon, mets tous les booléens à 'False'.    
"""

load_dotenv()
llm = ChatOpenAI(model = "gpt-4o", temperature=0)

def quality_control_agent(state: NewsletterState):
    print("[AGENT QUALITY CONTROL] Inspection des brouillons...")
    
    revision_count = state.get("revision_count", 0)
    
    if revision_count >= 2:
        print("⚠️ [QUALITY CONTROL] Limite de révisions atteinte.")
        dummy_report = QualityReport(revise_top_news=False, feedback_top_news="",revise_news=False, feedback_news="",revise_flash_news=False, feedback_flash_news="")
        return {
            "quality_report": dummy_report,
            "revision_count": revision_count + 1
        }

    drafts = ""
    if state.get("top_news_item"):
        drafts += f"--- TOP NEWS ---\n{state['top_news_item'].model_dump_json()}\n"
    if state.get("news_list"):
        drafts += f"--- NEWS ---\n{state['news_list'].model_dump_json()}\n"
    if state.get("flash_news_list"):
        drafts += f"--- FLASH NEWS ---\n{state['flash_news_list'].model_dump_json()}\n"

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "Voici les brouillons de cette édition :\n{drafts}")
    ])

    chain = prompt | llm.with_structured_output(QualityReport)
    report = chain.invoke({"drafts": drafts})

    errors_found = any([report.revise_top_news, report.revise_news, report.revise_flash_news])
    if errors_found:
        print("❌ [QUALITY CONTROL] Brouillons refusés ! Voici le bilan :")
        if report.revise_top_news: print(f"  - Top News : {report.feedback_top_news}")
        if report.revise_news: print(f"  - News : {report.feedback_news}")
        if report.revise_flash_news: print(f"  - Flashs : {report.feedback_flash_news}")
    else:
        print("✅ [QUALITY CONTROL] Tout est parfait !")

    return {
        "quality_report": report, 
        "revision_count": revision_count + 1
    }