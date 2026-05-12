from typing import TypedDict, List, Optional, Annotated
import operator

class NewsletterState(TypedDict) : 
    lookback_day : int
    urls : Annotated[List[dict], operator.add]
    articles : Annotated[List[dict], operator.add]