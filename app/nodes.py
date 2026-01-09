from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from app.config import llm
from app.state import GraphState
from app.tools import get_weather_data, retrieve_documents

# --- 1. Router Logic ---
class RouteQuery(BaseModel):
    """Route the user query to the most relevant datasource."""
    datasource: str = Field(
        ..., 
        description="Given a user question, choose to route it to 'weather' or 'rag'. Use 'weather' for current temperature/forecast. Use 'rag' for document questions."
    )

def router_node(state: GraphState):
    print("---ROUTER---")
    structured_llm = llm.with_structured_output(RouteQuery)
    result = structured_llm.invoke(state["question"])
    return {"route": result.datasource}

# --- 2. Tool Nodes ---

# Define a simple schema for City Extraction
class CityExtraction(BaseModel):
    city: str = Field(..., description="The name of the city mentioned in the query.")

def weather_node(state: GraphState):
    print("---FETCHING WEATHER---")
    question = state["question"]
    
    # 1. Extract the city using the LLM
    print(f"DEBUG: Extracting city from '{question}'...")
    extractor = llm.with_structured_output(CityExtraction)
    result = extractor.invoke(question)
    city_name = result.city
    
    print(f"DEBUG: Extracted City: {city_name}")
    
    # 2. Call the API with ONLY the city name
    try:
        weather_data = get_weather_data(city_name)
    except Exception as e:
        weather_data = f"Error fetching weather for {city_name}: {str(e)}"
        
    return {"context": weather_data}

def rag_node(state: GraphState):
    print("---RETRIEVING DOCS---")
    context = retrieve_documents(state["question"])
    return {"context": context}

# --- 3. Generator Node ---
def generation_node(state: GraphState):
    print("---GENERATING ANSWER---")
    prompt = ChatPromptTemplate.from_template(
        """You are a helpful assistant. Answer the user's question based ONLY on the following context.
        
        Context:
        {context}
        
        Question: 
        {question}
        """
    )
    chain = prompt | llm
    response = chain.invoke({"context": state["context"], "question": state["question"]})
    return {"answer": response.content}