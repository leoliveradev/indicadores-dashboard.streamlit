import streamlit as st
from components.navbar import render_navbar
from config.theme import STREAMLIT_CSS

def setup_page(current_page: str):
    st.markdown(STREAMLIT_CSS, unsafe_allow_html=True)
    render_navbar(current_page)