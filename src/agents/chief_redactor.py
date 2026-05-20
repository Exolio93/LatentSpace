from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from src.schema import IntroductionItem
from src.state import NewsletterState

load_dotenv()
llm = ChatOpenAI(model = "gpt-4o", temperature=0)

system_prompt = """

Tu es le Rédacteur en Chef de 'Latent Space'. 
Rédige l'introduction de la semaine. Sois chaleureux, analytique, et dégage la tendance 'macro' 
de la semaine sans faire une simple liste des articles.

"""


def chief_redactor_agent(state : NewsletterState) : 
    print("🎩 [RÉDACTEUR EN CHEF] Rédaction de l'introduction globale...")

    top_news = state.get("top_news_item")
    news_list = state.get("news_list")
    
    content = f"GRAND FORMAT : {top_news.title if top_news else 'Aucun'}\n"
    content += "AUTRES SUJETS :\n" + "\n".join([f"- {n.catch_phrase}" for n in news_list.items])

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "Voici le contenu de l'édition d'aujourd'hui :\n{content}\n\nGénère l'objet structuré de l'introduction.")
    ])

    chain = prompt | llm.with_structured_output(IntroductionItem)
    intro_item = chain.invoke({"content": content})

    print("🎩 [RÉDACTEUR EN CHEF] Introduction validée.")
    return {"introduction_item": intro_item}