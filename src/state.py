from typing import TypedDict, List, Optional, Annotated
import operator
from schema import EditionStructure, FlashNewsList, NewsList, TopNewsItem

class NewsletterState(TypedDict) : 
    lookback_day : int
    urls : Annotated[List[dict], operator.add]
    articles : Annotated[List[dict], operator.add]

    edition_structure : Optional[EditionStructure]
    
    top_news_item : Optional[TopNewsItem]
    news_list : Optional[NewsList]
    flash_news_list : Optional[FlashNewsList]