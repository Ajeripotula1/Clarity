import streamlit as st
import requests
import mimetypes

st.set_page_config(page_title="Clarity", page_icon=":brain:",layout="centered")
st.title("📤 Upload")
st.markdown("Upload your notes for summaries, Q&A, and flashcard generation.")
# File Upload
uploaded_file = st.file_uploader("", type=["txt","pdf"])
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
        # query = st.text_input("Ask questions based on your notes: ")
        # if query:
        #     with st.spinner("Thinking..."):
        #         query_url = "http://localhost:8000/ask" 

        #         response = requests.post(query_url, json={"query":query})
        #         result = response.json()
        #         st.write("**Answer:**", result['answer'])
        #         with st.expander("Sources"):
        #             for source in result["sources"]:
        #                 st.write(source)
    else:
        st.error(f"❌ Failed to process the file: {response.text}")