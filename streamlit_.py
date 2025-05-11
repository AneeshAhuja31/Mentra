import streamlit as st
import requests
st.set_page_config(page_title="Mentra",page_icon="😈",layout="centered")


hide_sidebar_style = """
    <style>
        [data-testid="stSidebarCollapsedControl"] {
            display: none;
        }
        [data-testid="stSidebar"] {
            display: none;
        }
        [data-testid="collapsedControl"] {
            display: none;
        }
        [class="st-emotion-cache-6qob1r e19011e68"] {
            display: none;
        }
        [class="st-emotion-cache-79elbk e19011e61"] {
            display: none;
        }
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)


st.title("Mentra")
st.markdown("""Welcome to Mentra - Your Career Companion!
Enhance your resume, get personalized feedback, and receive expert job advice with our smart chatbot. Whether you’re building your first resume or optimizing an existing one, we’ve got you covered.
""")
if st.button("Get Started"):
    st.switch_page("pages/login_.py")