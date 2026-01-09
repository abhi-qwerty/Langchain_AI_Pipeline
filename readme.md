# 🤖 Agentic AI Pipeline: Weather & RAG Agent

A robust, production-ready AI agent built with **LangGraph**, **Google Gemini 2.5 Flash**, and **Qdrant**. This application demonstrates an "Explicit Router" architecture that intelligently decides whether to fetch real-time weather data or retrieve answers from a PDF document.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-v0.3-green)
![Gemini](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)

## 🏗️ Architecture

The system uses an **Explicit Router** pattern to eliminate hallucinated tool calls.


1.  **Router Node**: Analyzes user intent (Weather vs. Document Query) using Structured Output (Pydantic models).
2.  **Weather Node**: 
    * Extracts specific city names using LLM reasoning (e.g., converts "What's the temp in the Big Apple?" -> "New York").
    * Calls the OpenWeatherMap API.
3.  **RAG Node**: 
    * Retrieves context from a local Qdrant Vector Database.
    * Uses **text-embedding-004** for high-quality vector search.
4.  **Generator Node**: Synthesizes the final response using the retrieved context.

---

## 🧠 Main Overview

The system is designed with a "Router-First" approach to ensure precision:

### 1. The Router (Decision Maker)
* **File:** `app/nodes.py` (`router_node`)
* **Function:** Analyzes the user's question using a structured schema.
* **Logic:** Returns a strict `"weather"` or `"rag"` routing decision, ensuring the agent never tries to "guess" a tool usage.

### 2. The Tools (Skills)
* **Weather Tool:** * Includes an **Intelligence Layer** that extracts specific city names (e.g., converts "weather in the Big Apple" -> "New York") before calling the OpenWeatherMap API.
* **RAG Tool:** * Uses **Qdrant** (Local Mode) for vector storage.
    * Retrieves the top 10 chunks (`k=10`) using `text-embedding-004` for high-fidelity context.

### 3. State Management
* **File:** `app/state.py`
* **Function:** Uses a typed `GraphState` dictionary to pass data (Question -> Route -> Context -> Answer) between nodes, ensuring type safety throughout the graph execution.

### 4. The Interface (Frontend)
* **File:** `ui.py`
* **Framework:** Streamlit.
* **Features:** * Sidebar for PDF ingestion.
    * Real-time processing logs.
    * Auto-reconnect logic for the database.

---

## 📂 Project Structure

```text
ai_pipeline_project/
├── .env                     # Environment variables (API Keys)
├── requirements.txt         # Python Dependencies
├── ui.py                    # Streamlit Entry Point (Frontend)
├── data/                    # Temporary storage for uploaded PDFs
├── qdrant_db/               # Local Vector Database (Persistent)
└── app/                     # Core Application Logic
    ├── __init__.py
    ├── config.py            # Service Account & Model Config
    ├── graph.py             # LangGraph Workflow Definition
    ├── nodes.py             # Logic for Router, Weather, RAG, Generator
    ├── state.py             # GraphState Type Definition
    ├── tools.py             # API Wrappers for Weather & Retrieval
    └── vector_store.py      # Qdrant Ingestion (with Rate Limiting)
```

## ✅ What This Meets

- [x] **Correct integration of LangGraph & LangChain**
- [x] **Proper decision-making within nodes** (Explicit Router)
- [x] **Working Vector Database** (Qdrant with local persistence)
- [x] **Clean, modular code structure**
- [x] **Effective LangSmith evaluation script included**
- [x] **Rate Limit Handling** (Automatic batching & sleep)
- [x] **Functional Streamlit UI** (with chat interface)

---

## ▶️ How to Run

### 1. Prerequisites

Make sure you have the following installed and configured:

- Python **3.11+**
- Google API Key
- OpenWeatherMap API Key (Free tier)
- Langsmith API Key (Free tier)

---

### 2. Setup

Clone the repository and install dependencies:

```bash
git clone https://github.com/abhi-qwerty/Langchain_AI_Pipeline.git
cd Langchain_AI_Pipeline
python -m venv venv
pip install -r requirements.txt
```
---

### 3. Add relevent API Keys in .env file
```text
GOOGLE_API_KEY=your_google_api_key
OPENWEATHERMAP_API_KEY=your_openweathermap_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=gemini-agent-demo
```
---

## 4. ▶️ Run the Agent

Start the Streamlit application using the following command:

```bash
streamlit run ui.py
```

Once the application starts, Streamlit will display a local URL in the terminal (usually):

```bash
streamlit run ui.py
```
## 🧠 What You Can Do

### 🌦 Ask Weather-Related Questions
The agent can query real-time weather data.
* **Example:** *"What is the weather in New York?"*

### 📄 Upload & Query PDFs
Upload any PDF document through the user interface to chat with your data.
* **Upload:** Upload your PDF file and ingest it into vector DB.
* **Ask:** Ask questions related to the specific content of the uploaded file.
* **Result:** The AI retrieves relevant sections from the document to provide accurate answers.

---
