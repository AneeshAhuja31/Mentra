import streamlit as st
import requests
if "request_session" not in st.session_state:
    st.session_state.requests_session = requests.Session()

st.set_page_config(page_title="Mentra",page_icon="😈",layout="centered")

st.title("Mentra")
st.markdown("""Welcome to Mentra - Your Career Companion!
Enhance your resume, get personalized feedback, and receive expert job advice with our smart chatbot. Whether you’re building your first resume or optimizing an existing one, we’ve got you covered.
""")
if st.button("Get Started"):
    st.switch_page("pages/login_.py")