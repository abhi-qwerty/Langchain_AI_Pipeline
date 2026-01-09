from langchain_community.utilities import OpenWeatherMapAPIWrapper
from app.vector_store import get_retriever

# 1. Weather Tool
weather_wrapper = OpenWeatherMapAPIWrapper()

def get_weather_data(city: str) -> str:
    return weather_wrapper.run(city)

# 2. RAG Retrieval Tool
def retrieve_documents(query: str) -> str:
    retriever = get_retriever()
    
    # Invoke retrieval
    docs = retriever.invoke(query)
    
    if not docs:
        return "No relevant documents found in the database. (Is the PDF ingested?)"
        
    # Format the output
    return "\n\n".join([d.page_content for d in docs])