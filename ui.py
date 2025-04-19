import streamlit as st
import requests
import mimetypes

# Streamlit Frontend

# Basic UI 
st.set_page_config(page_title="Clarity",layout="centered")
st.title("Clarity 🧠")
st.markdown("An AI-powered second brain. Upload your notes — Clarity will read them, understand your style, and help you study smarter by generating summaries, flashcards, and personalized answers.")

# File Upload
uploaded_file = st.file_uploader("Upload your notes", type=["txt","pdf"])
if uploaded_file:
    mime_type, _ = mimetypes.guess_type(uploaded_file.name) # Dyamically determine media type
    if not mime_type:
        mime_type = "application/octet-stream"  # Fallback
    files = {"file": (uploaded_file.name, uploaded_file,mime_type)}
    
    # Send file to FastAPI for processing
    api_url = "http://localhost:8000/upload" 
    response = requests.post(api_url, files=files)
    
    if response.status_code == 200:
        st.success("✅ File processed successfully!")
        query = st.text_input("Ask questions based on your notes: ")
        if query:
            with st.spinner("Thinking..."):
                query_url = "http://localhost:8000/ask" 

                response = requests.post(query_url, json={"query":query})
                result = response.json()
                st.write("**Answer:**", result['answer'])
                with st.expander("Sources"):
                    for source in result["sources"]:
                        st.write(source)
    else:
        st.error(f"❌ Failed to process the file: {response.text}")

