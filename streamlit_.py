import streamlit as st
import requests

st.set_page_config(page_title="Mentra", page_icon="〽️", layout="centered")

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

st.markdown("<h1 style='text-align: center; color: #FFD700; font-size: 3.5rem; font-weight: bold;'>〽️entra</h1>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; margin-bottom: 30px;">
    <p>Welcome to Mentra - Your Career Companion!</p>
    <p>Enhance your resume, get personalized feedback, and receive expert job advice with our smart chatbot.</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("#### 📄 Resume Analysis")
        st.write("Get personalized feedback on your resume and suggestions for improvements.")

with col2:
    with st.container(border=True):
        st.markdown("#### 🤖 AI Career Mentor")
        st.write("Chat with our AI to get tailored career advice, job search strategies, and industry insights.")

col3, col4 = st.columns(2)

with col3:
    with st.container(border=True):
        st.markdown("#### 🧠 Skill Assessment")
        st.write("Test your knowledge with adaptive quizzes to identify strengths and areas for improvement.")

with col4:
    with st.container(border=True):
        st.markdown("#### 📊 Performance Tracking")
        st.write("Track your progress over time with detailed metrics and personalized recommendations.")

st.markdown("---")
st.markdown("<h3 style='text-align: center; color: #FFD700;'>Why Choose Mentra?</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Our AI-powered platform offers personalized guidance that evolves with your career journey. Upload your resume once and unlock a suite of tools designed to help you succeed.</p>", unsafe_allow_html=True)

st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Get Started", type="primary", use_container_width=True):
        st.switch_page("pages/login_.py")