from typing import TypedDict, Optional

class GraphState(TypedDict):
    question: str          # User input
    context: Optional[str] # Data fetched from RAG or Weather
    answer: Optional[str]  # Final generated answer
    route: Optional[str]   # "weather" or "rag"