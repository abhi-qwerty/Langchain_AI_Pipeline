import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

load_dotenv()

# Initialize Gemini Model
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# Initialize Embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# Qdrant Local Path
VECTOR_DB_PATH = "./qdrant_db"
COLLECTION_NAME = "my_docs"