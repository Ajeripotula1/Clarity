import streamlit as st
import requests
# st.set_page_config(page_title="Clarity", page_icon=":brain:",layout="centered")
st.title("💬 Chat with Your Notes")

# Initialize chat history in session
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    
# Send chat + history to backend
def send_query(query):
    API_URL = "http://localhost:8000/chat"  
    # Format chat history for the backend 
    payload = {
        "query" : query,
        "chat_history" : st.session_state.chat_history
    }
    try:
        res = requests.post(API_URL, json=payload)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")
        return None 

# Input box for user query
# Correct usage
user_query = st.chat_input("Your Question:")


if user_query:
    # Add user message to session state
    st.session_state.chat_history.append({"role":"user", "content":user_query})
    
    # Send to backend
    result = send_query(user_query)
    
    if result:
        # Add assistant response to history
        assistant_reply = result["answer"]
        st.session_state.chat_history.append({"role":"assistant", "content":assistant_reply})

# Display full chat history
for turn in st.session_state.chat_history:
    with st.chat_message(turn["role"]):
        st.markdown(turn["content"])

        