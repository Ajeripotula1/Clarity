import streamlit as st
import requests

# st.set_page_config(page_title="Clarity", page_icon=":brain:",layout="centered")
st.title("Remove Documents")
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
        res = requests.get(API_URL + "documents")
        res.raise_for_status()
        data = res.json() # parse json response
        return data.get("file_names",[])

    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")
        return [] 
def delete_doc(doc_name):
    try:
        payload = {
            "file_name": doc_name
        }
        res = requests.post(API_URL+"delete",json=payload)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")
        return False 

docs = query_docs()
if docs:
    st.subheader("🗑️ Click a document to delete it")

    for doc in docs:
        # Wrap each button in a full-width container
        container = st.container()
        with container:
            if st.button(f"{doc}", key=doc):
                reponse = delete_doc(doc)
                if reponse and reponse.get("success"):
                    st.success("File Deleted Successfully.")
                    st.rerun()
                else:
                    st.error("Unable to delete file.")
else:
    st.info("No documents found.")