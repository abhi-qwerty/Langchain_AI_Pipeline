import os
import time
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from app.config import embeddings, VECTOR_DB_PATH, COLLECTION_NAME

# --- 1. CACHED CLIENT (The Fix) ---
# This ensures the connection stays alive across Streamlit reruns
@st.cache_resource
def get_qdrant_client():
    """Returns a cached instance of the Qdrant Client."""
    # Ensure the directory exists to prevent errors
    if not os.path.exists(VECTOR_DB_PATH):
        os.makedirs(VECTOR_DB_PATH)
    
    client = QdrantClient(path=VECTOR_DB_PATH)
    return client

def ingest_pdf(pdf_path: str):
    """Reads PDF, chunks it, and stores in Qdrant with Rate Limiting."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found at {pdf_path}")

    print("📄 Loading PDF...")
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    print(f"💽 Found {len(splits)} chunks. Starting batched ingestion...")
    
    client = get_qdrant_client()
    
    # Check/Create collection
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )

    vector_store = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
    )
    
    # --- RATE LIMITING LOGIC (Keep this from before) ---
    batch_size = 5
    total_batches = (len(splits) + batch_size - 1) // batch_size
    
    for i in range(0, len(splits), batch_size):
        batch = splits[i : i + batch_size]
        print(f"   Processing batch {i//batch_size + 1}/{total_batches}...")
        vector_store.add_documents(documents=batch)
        time.sleep(2) # Prevent 429 Error
    
    print("✅ Ingestion Complete!")

def get_retriever():
    """Returns the vector store retriever using the cached client."""
    client = get_qdrant_client()
    
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
    )
    
    # IMPROVEMENT: Increase 'k' to get more context
    return vector_store.as_retriever(search_kwargs={"k": 10})