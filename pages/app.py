import streamlit as st
from streamlit import Page, navigation

# Global configurations for app
st.set_page_config(page_title="Clarity", page_icon=":brain:",layout="centered")

# Define the different Pages as objects
pages = [
    Page("home.py", title="Home", icon="🏠"),
    Page("upload.py", title="Upload", icon="📤"),
    Page("summarize.py", title="Summarize", icon="📝"),
    Page("chat.py", title="Chat", icon="💬"),
    Page("flashcards.py", title="Flashcards", icon="🗂️"),
    Page("remove.py", title="Remove", icon="🗑️"),
]

# Configure available pages and run selected
nav = navigation(pages=pages)
nav.run()