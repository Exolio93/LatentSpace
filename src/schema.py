from pydantic import BaseModel, Field, HttpUrl
from typing import List

flashnews_min = 5
flashnews_max = 8
news_min = 3
news_max = 3

class IntroductionItem(BaseModel):
    # 1. L'accueil
    mot_de_bienvenue: str = Field(
        ..., 
        description="Une phrase d'accueil chaleureuse ou percutante pour ouvrir la newsletter (ex: 'Bonjour à tous, préparez votre café ☕').",
        max_length=100
    )
    
    # 2. L'indicateur d'humeur / Le ton
    meteo_de_la_semaine: str = Field(
        ...,
        description="Un ou deux emojis suivis d'un ou deux mots pour donner la température du marché ou de l'actu (ex: '🌪️ Zone de turbulences', '🐢 Calme plat', '🚀 Semaine historique').",
        max_length=50
    )
    
    # 3. Le résumé des tendances
    resume_tendances: str = Field(
        ..., 
        description=(
            "Un paragraphe de 2 à 3 phrases maximum qui résume les grandes dynamiques de la semaine. "
            "Ne donne pas les détails des articles, survole l'actualité de très haut pour lier les sujets entre eux."
        ),
        min_length=150,
        max_length=450
    )

class TopNewsItem(BaseModel):

    title: str = Field(
        ...,
        description="Un titre très court et percutant." ,
        max_length=50)

    # 1. L'entrée en matière
    catchphrase: str = Field(
        ..., 
        description="Une phrase d'accroche très courte et percutante pour capter l'attention instantanément.",
        max_length=80)
    
    # 2. Le "Pourquoi maintenant ?"
    trigger: str = Field(
        ...,
        description="Le point de départ de l'actualité. Pourquoi on en parle aujourd'hui ? Rédigé sur un ton direct et conversationnel. (environ 3 à 4 phrases).",
        min_length=150,
        max_length=300)
    
    # 3. Le coeur du sujet
    fact: str = Field(
        ...,
        description="Les faits concrets, les chiffres clés ou le rapport de force. C'est la partie purement informative et factuelle. (environ 3 à 4 phrases).",
        min_length=200,
        max_length=400)
    
    # 4. L'analyse
    big_picture: str = Field(
        ...,
        description="La prise de recul. En quoi cette actualité s'inscrit dans une tendance de fond du marché ou de la société ? (environ 3 phrases).",
        min_length=150,
        max_length=350)
    
    # 5. La conclusion
    end_word: str = Field(
        ...,
        description="Une conclusion ultra-rapide en 1 ou 2 phrases qui résume la situation ou ouvre sur l'avenir, souvent avec une touche d'ironie ou de légèreté.",
        max_length=150)

class PaperItem(BaseModel):

    # 1. Le vrai nom
    title: str = Field(
        ...,
        description="Le vrai titre scientifique en anglais (ex: 'Attention Is All You Need').")
    
    # 3. Le "Quoi" (La découverte)
    what: str = Field(
        ...,
        description="L'idée principale ou la découverte du papier expliquée simplement. Qu'ont-ils trouvé ? (environ 3 phrases max).",
        min_length=150,
        max_length=350)
    
    # 4. Le "Comment" (La méthode vulgarisée)
    how: str = Field(
        ...,
        description="Comment les chercheurs ont-ils prouvé cela ? Explique la méthodologie avec une analogie si possible, sans termes techniques obscurs. (2 à 3 phrases).",
        min_length=100,
        max_length=300)
    
    # 5. Le "Et alors ?" (L'impact)
    impact: str = Field(
        ...,
        description="Les implications concrètes. En quoi cette recherche pourrait changer notre quotidien, notre industrie ou nos technologies d'ici quelques années ? (environ 3 phrases).",
        min_length=150,
        max_length=350)
    
    # 6. Les sources
    url: HttpUrl = Field(
        ...,
        description="Le lien direct vers l'étude (arXiv, Nature, etc.).")

class NewsItem(BaseModel):
    # L'accroche visuelle (Emoji + Titre)
    catch_phrase: str = Field(
        ..., 
        description="Un emoji suivi d'un titre thématique très court de 2 ou 3 mots (ex: '🕵️ Agent double', '⛽ Opération Kérosène').",
        max_length=40)
    
    # Le corps du texte
    content: str = Field(
        ..., 
        description=(
            "Un paragraphe unique et fluide qui raconte l'actualité. "
            "Il doit inclure le contexte, le fait marquant et la conséquence. "
            "IMPORTANT : Mets en gras (avec **) quelques mots clés pour faciliter la lecture."
        ),
        min_length=400,
        max_length=900)

class NewsList(BaseModel) : 
    items: List[NewsItem] = Field(
        ..., 
        min_length=news_min, 
        max_length=news_max,
        description="Une liste de 3 actualités de taille moyenne pour couvrir les informations importantes."
    )

class FlashNewsItem(BaseModel):
    entity: str = Field(
        ..., 
        description="L'entreprise, la personne ou l'institution au coeur de l'info (ex: 'McDonald\\'s', 'La Norges Bank', 'Les négociateurs européens').",
        max_length=50
    )
    content: str = Field(
        ..., 
        description="L'action, le chiffre ou le fait marquant, en une seule phrase très courte et sans fioritures.",
        max_length=150 
    )

class FlashNewsList(BaseModel) :
    items: List[FlashNewsItem] = Field(
        ..., 
        min_length=flashnews_min, 
        max_length=flashnews_max,
        description="Une liste de 5 à 8 actualités très courtes pour balayer le reste de l'information."
    )

# Schema final 

class LatentSpace(BaseModel) : 
    numero_edition : int
    email_object : str

    introduction : IntroductionItem

    top_news : TopNewsItem
    news : NewsList
    flash_news : FlashNewsList
    #paper : PaperItem

########################
# Schema pour l'editeur
########################

class Subject(BaseModel):
    title: str = Field(description="Titre temporaire pour comprendre le sujet.")
    urls_sources: List[str] = Field(description="Les URLs exactes des articles scrappés à utiliser pour ce sujet.")
    editorial_perspective: str = Field(description="Une phrase pour dire au rédacteur sous quel angle traiter l'info.")


class EditionStructure(BaseModel) : 
    top_news_subject : Subject = Field(description="L'actualité la plus importante et complexe de la semaine.")
    news_subject : List[Subject] = Field(min_length=3, max_length=3,description="Exactement 3 sujets secondaires mais impactants.")
    flash_news_subject : List[Subject] = Field(min_length=5, max_length=8,description="5 à 8 actualités très courtes pour le balayage final.")

