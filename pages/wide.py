import streamlit as st

def wide_page():
    st.markdown(
        """
        <style>
            .block-container {
                max-width: 1200px;
                margin: auto;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

wide_page()
