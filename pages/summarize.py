import streamlit as st
import requests
# st.set_page_config(page_title="Clarity", page_icon=":brain:",layout="centered")

st.title("📝 Summarize")

# CSS to make all buttons same width and prevent text wrap
st.markdown("""
<style>
.stButton > button {
    width: 80%;
    height: 3em;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)

API_URL = "http://localhost:8000/"
def query_docs():
    try:
        res = requests.get(API_URL +"documents")
        res.raise_for_status()
        data = res.json() # parse json response
        return data.get("file_names", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")
        return []

def summarize_doc(doc_name):
    try:
        payload = {
            "file_name": doc_name
        }
        res = requests.post(API_URL + "summarize", json=payload)
        res.raise_for_status()
        data = res.json()
        return data.get("answer", "No summary for selected file")
    except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")
            return("")

docs = query_docs()
summary = ''
if docs:
    st.subheader("Select a document to summarize:")
    for doc in docs:
        container = st.container()
        with container:
             if st.button(f"{doc}", key=doc):
                summary = summarize_doc(doc)
    st.markdown(summary)