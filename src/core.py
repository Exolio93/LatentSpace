from langgraph.graph import StateGraph, START, END
from agents import chief_redactor
from agents.chief_redactor import chief_redactor_agent
from agents.quality_control import quality_control_agent
from agents.redactors import flash_news_redactor_agent, news_redactor_agent, top_news_redactor_agent
from agents.sourcing import soursing_agent
from agents.chief_editor import chief_editor_agent
from state import NewsletterState
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
    workflow.add_edge(["top_news_redactor", "news_redactor", "flash_news_redactor"], "quality_control")

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
    plan = result.get("edition_structure")

    with open("debug_plan.json", "w", encoding="utf-8") as f:
        f.write(plan.model_dump_json(indent=4))

    content_dict = {k: v.model_dump() for k, v in result.items() if hasattr(v, 'model_dump')}

    with open("debug_content.json", "w", encoding="utf-8") as f:
        json.dump(content_dict, f, indent=4, ensure_ascii=False)