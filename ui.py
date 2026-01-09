import streamlit as st
import os
from dotenv import load_dotenv

# 1. LOAD ENV VARS FIRST
# We use override=True so that if you change .env while the app is running, 
# the reset button will actually pick up the new keys.
load_dotenv(override=True)

# Check if keys are actually loaded
if not os.getenv("OPENWEATHERMAP_API_KEY"):
    st.error("⚠️ OPENWEATHERMAP_API_KEY not found in environment variables!")

# Now import the rest of the app
# (Note: errors in these imports might still crash the app before the UI loads if env vars are missing initially)
from app.graph import build_graph
from app.vector_store import ingest_pdf

st.set_page_config(page_title="Gemini Agent", page_icon="🤖")

st.title("🤖 LangGraph Agent: Weather & RAG")

# Sidebar for Setup
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # RESET BUTTON
    if st.button("🔄 Reset State & Reload"):
        st.session_state.clear()
        load_dotenv(override=True)
        st.rerun()
    
    st.divider()
    
    # DB STATUS CHECK
    if os.path.exists("./qdrant_db") and os.path.isdir("./qdrant_db"):
        st.success("✅ Database detected on disk.")
    else:
        st.warning("⚠️ No Database found. Please ingest a PDF.")

    uploaded_file = st.file_uploader("Upload a PDF for RAG", type="pdf")
    
    if uploaded_file and st.button("Ingest PDF"):
        save_path = f"./data/{uploaded_file.name}"
        os.makedirs("./data", exist_ok=True)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        with st.spinner("Ingesting chunks into Qdrant..."):
            # We catch the lock error gracefully here
            try:
                ingest_pdf(save_path)
                st.success("PDF Processed!")
            except Exception as e:
                st.error(f"Error ingesting PDF: {e}")

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask about weather or your PDF..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process through LangGraph
    try:
        app = build_graph()
        inputs = {"question": prompt}
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            final_answer = ""
            
            # Stream the response
            for output in app.stream(inputs):
                for key, value in output.items():
                    if "answer" in value:
                        final_answer = value["answer"]
            
            if final_answer:
                message_placeholder.markdown(final_answer)
            else:
                message_placeholder.markdown("⚠️ No answer generated. Check logs.")
        
        st.session_state.messages.append({"role": "assistant", "content": final_answer})
        
    except Exception as e:
        st.error(f"An error occurred: {e}")