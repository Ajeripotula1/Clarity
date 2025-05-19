import streamlit as st
import requests
# from wide import wide_page
# wide_page()
# st.set_page_config(page_title="Clarity", page_icon=":brain:",layout="wide")

API_URL = "http://localhost:8000/flashcards"

st.title("📚 AI-Generated Flashcards")

st.markdown("""
<style>
 .block-container {
                max-width: 1000px;
                margin: auto;
            }
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
        res = requests.get(API_URL+"documents")
        res.raise_for_status()
        data = res.json() 
        return data.get("file_names",[])
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")
        return []
    
def get_flashcards(file_name):
    try:    
        response = requests.post(API_URL+"flashcards", json={"file_name": file_name})

        response.raise_for_status()
        flashcards = response.json()["flash_cards"]
        st.session_state["flashcards"] = flashcards

        # Initialize flip states
        st.session_state["flips"] = {i: False for i in range(len(flashcards))}
    except Exception as e:
        st.error(f"Error: {str(e)}")


# Initialize session state
if "flashcards" not in st.session_state:
    st.session_state["flashcards"] = []
if "flips" not in st.session_state:
    st.session_state["flips"] = {}
    
docs = query_docs()
summary = ''
if docs:
    st.subheader("Select a document to generate Flashcards:")
    for doc in docs:
        container = st.container()
        with container:
             if st.button(f"{doc}", key=doc):
                flashcards = get_flashcards(doc)
    st.markdown(summary)



# Display flashcards if available
if st.session_state["flashcards"]:
    st.subheader("🃏 Flashcards")

    cols = st.columns(3)  # 3 cards per row

    for i, card in enumerate(st.session_state["flashcards"]):
        with cols[i % 3]:
            st.markdown("----")
            flip_key = f"flip_{i}"

            if st.button("🔁 Flip", key=f"btn_{i}"):
                st.session_state["flips"][i] = not st.session_state["flips"].get(i, False)

            if not st.session_state["flips"].get(i, False):
                st.markdown(f"**Q{i+1}:** {card['question']}")
            else:
                st.markdown(f"**A{i+1}:** {card['answer']}")
