from langgraph.graph import StateGraph, START, END
from src.agents.chief_redactor import chief_redactor_agent
from src.agents.chief_redactor import chief_redactor_agent
from src.agents.quality_control import quality_control_agent
from src.agents.redactors import flash_news_redactor_agent, news_redactor_agent, top_news_redactor_agent
from src.agents.sourcing import soursing_agent
from src.agents.chief_editor import chief_editor_agent
from src.schema import LatentSpace
from src.state import NewsletterState
import json



def routing_function(state: NewsletterState):
    """
    Lit le rapport qualité et décide si on avance vers l'intro
    ou si on renvoie les brouillons aux rédacteurs fautifs.
    """
    report = state.get("quality_report")

    if not report:
        return "chief_redactor"
        
    nodes_to_rerun = []
    if getattr(report, "revise_top_news", False):
        nodes_to_rerun.append("top_news_redactor")
    if getattr(report, "revise_news", False):
        nodes_to_rerun.append("news_redactor")
    if getattr(report, "revise_flash_news", False):
        nodes_to_rerun.append("flash_news_redactor")
        
    if not nodes_to_rerun:
        return "chief_redactor"
        
    return nodes_to_rerun


def generate_newsletter():
    workflow = StateGraph(NewsletterState)

    workflow.add_node("sourcing", soursing_agent)
    workflow.add_node("chief_editor", chief_editor_agent)
    workflow.add_node("top_news_redactor", top_news_redactor_agent)
    workflow.add_node("news_redactor", news_redactor_agent)
    workflow.add_node("flash_news_redactor", flash_news_redactor_agent)
    workflow.add_node("quality_control", quality_control_agent)
    workflow.add_node("chief_redactor", chief_redactor_agent)

    workflow.add_edge(START, "sourcing")
    workflow.add_edge("sourcing", "chief_editor")
    workflow.add_edge("chief_editor", "top_news_redactor")
    workflow.add_edge("chief_editor", "news_redactor")
    workflow.add_edge("chief_editor", "flash_news_redactor")
    workflow.add_edge("top_news_redactor", "quality_control")
    workflow.add_edge("news_redactor", "quality_control")
    workflow.add_edge("flash_news_redactor", "quality_control")
    workflow.add_conditional_edges(
        "quality_control", 
        routing_function, 
        {
            "chief_redactor": "chief_redactor",
            "top_news_redactor": "top_news_redactor",
            "news_redactor": "news_redactor",
            "flash_news_redactor": "flash_news_redactor"
        }
    )
    workflow.add_edge("chief_redactor", END)

    app = workflow.compile()

    # ===================

    inputs =  {
        "lookback_day" : 7,
        "urls" : [],
        "articles" : []
    }

    print("🚀 Lancement du pipeline...")
    result = app.invoke(inputs)

    return LatentSpace(
        introduction=result.get("introduction_item"),
        top_news=result.get("top_news_item"),
        news=result.get("news_list"),
        flash_news=result.get("flash_news_list")
    )
