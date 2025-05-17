import streamlit as st

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
    <h2>🚀 Welcome to <span style="color: #FFD700;">Mentra</span> – Your Ultimate Career Companion!</h2>
    <p style="font-size: 1.1rem; color: #aaa;">Supercharge your career with AI-driven resume enhancement, personalized feedback, and expert job-hunting advice.</p>
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

# Add social links section

st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Get Started", type="primary", use_container_width=True):
        st.switch_page("pages/login_.py")

st.markdown("---")
st.markdown("""
<div style="text-align: center; margin-top: 10px; margin-bottom: 20px;">
    <p style="font-size: 1rem; color: #aaa;">Connect with me</p>
    <div>
        <a href="https://github.com/AneeshAhuja31" target="_blank" style="text-decoration: none; margin: 0 10px;">
            <img src="https://github.com/fluidicon.png" width="32" height="32" alt="GitHub" style="vertical-align: middle;">
            <span style="color: #FFD700; vertical-align: middle; margin-left: 5px;">GitHub</span>
        </a>
        <a href="https://www.linkedin.com/in/aneesh-ahuja-9600a6291/" target="_blank" style="text-decoration: none; margin: 0 10px;">
            <img src="https://content.linkedin.com/content/dam/me/business/en-us/amp/brand-site/v2/bg/LI-Bug.svg.original.svg" width="32" height="32" alt="LinkedIn" style="vertical-align: middle;">
            <span style="color: #FFD700; vertical-align: middle; margin-left: 5px;">LinkedIn</span>
        </a>
    </div>
</div>
""", unsafe_allow_html=True)