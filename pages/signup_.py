import streamlit as st
import requests

hide_sidebar_style = """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        [data-testid="collapsedControl"] {
            display: none;
        }
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "signup_success" not in st.session_state:
    st.session_state.signup_success = False



if st.session_state.authenticated == True:
    session_id = st.session_state.session_id
    cookie = {"session_id":session_id}
    response = requests.get("http://127.0.0.1:8000/validate_session",cookies=cookie)
    if response.status_code == 200:
        body = response.json()
        if body.get("authenticated",True):
            st.session_state.authenticated = True
            st.session_state.username = body.get("username")
            st.switch_page("pages/dashboard.py")

@st.cache_resource
def get_cached_session():
    if "cached_session" not in st.session_state:
        st.session_state.cached_session= {
            "authenticated":False,
            "username":None,
            "session_id":None
        }
    return st.session_state.cached_session

def update_session_cache():
    st.session_state.cached_session = {
        "authenticated":st.session_state.authenticated,
        "username":st.session_state.username,
        "session_id":st.session_state.session_id
    }
    get_cached_session.clear()
    get_cached_session()

cached_session = get_cached_session()
if cached_session.get('authenticated',False) == True:
    st.switch_page("pages/dashboard.py")

with st.container (border= True):
    st.subheader("Signup")
    username = st.text_input("Enter username")
    password = st.text_input("Enter password",type="password")
    reenterpassword = st.text_input("Renter password",type="password")
    if st.button("Signup"):
        if password != reenterpassword:
            st.error("Enter matching password")
        else:
            request = {
                "username":username,
                "password":password
            }
            response = requests.post("http://127.0.0.1:8000/signup",json=request)
            if response.status_code ==200:
                response_data = response.json()
                if response_data.get("result"):
                    st.success(response_data.get("message"))
                    st.session_state.signup_success = True
                else:
                    st.error(response_data.get("message"))
    
    if st.session_state.signup_success:
        if st.button("Login"):
            st.switch_page("pages/login_.py")

        