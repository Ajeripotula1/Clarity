# Introduction Page + Navigation features
import streamlit as st
# st.set_page_config(page_title="Clarity", page_icon=":brain:",layout="centered")
# Content 
st.title("🧠📝 Clarity")
st.markdown('''An **AI-powered** second brain. Upload your notes — Clarity will read them, 
            understand your style, and help you study smarter by generating summaries, 
            flashcards, and personalized answers to your questions. 
            Clarity gives you the tools to turn passive notes into active learning.''')
st.markdown("""Clarity stands out from other document summarization apps by thinking with your material. It blends contextual awareness with AI reasoning te deliver relevant, thoughtful answers.

Built with OpenAI LLM, RAG, and LangChain.""")
st.markdown("""
## ✨ Features

- 📂 **Upload Files** — Add `.txt` and `.pdf` files to your knowledge base
- 🔍 **Searchable Memory** — Uses embeddings + vector search for retrieval
- 💬 **Chat with Your Notes** — Ask anything. Clarity will prioritize your uploaded notes, but if it finds gaps, it fills them using reliable general knowledge — just like a great tutor would.
- 🧠 **Smart Summaries** — Tired of reading dense paragraphs? Get clean concise summaries outlining Big Ideas, Key terms, and TL;DR-style takeaways.
- 🎓 **Flashcard Generator** — Turn any document into interactive flashcards with one click — perfect for spaced repetition and active recall.
- 🌐 **Frontend UI** — Clean, minimal, and modularized UI for quick interactions


##### Use the sidebar to navigate to a feature and get started!
""")


