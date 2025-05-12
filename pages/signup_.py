import streamlit as st
import requests
st.set_page_config(page_title="Signup",page_icon="〽️",layout="centered")

hide_sidebar_style = """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        [data-testid="collapsedControl"] {
            display: none;
        }
        [data-testid="stSidebarCollapsedControl"] {
            display: none;
        }
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

@st.cache_resource
def get_cached_session():
    if "cached_session" not in st.session_state:
        st.session_state.cached_session= {
            "authenticated":False,
            "username":None,
            "session_id":None,
            "chats":{},
            "active_chat_id":None,
            "current_chat_history":[]
        }
    return st.session_state.cached_session

def update_session_cache():
    st.session_state.cached_session = {
        "authenticated":st.session_state.authenticated,
        "username":st.session_state.username,
        "session_id":st.session_state.session_id,
        "chats":st.session_state.get("chats",{}),
        "active_chat_id":st.session_state.get("active_chat_id",None),
        "current_chat_history":st.session_state.get("current_chat_history",[])

    }
    get_cached_session.clear()
    get_cached_session()

def verify_session():
    try:
        session_id = st.session_state.get("session_id",None)
        if not session_id:
            st.session_state.authenticated = False
            st.session_state.username = None
            update_session_cache()
            return False
        
        cookie = {"session_id":session_id}
        try:
            response = requests.get("http://127.0.0.1:8000/validate_session",cookies=cookie)

            if response.status_code == 200:
                data = response.json()
                if data["authenticated"]:
                    st.session_state.authenticated = True
                    st.session_state.username = data.get("username")
                    update_session_cache()
                    return True
                
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.session_id = None
                update_session_cache()
                return False
        except requests.exceptions.RequestException:
            return st.session_state.authenticated
    except Exception:
        return st.session_state.authenticated

cached_session = get_cached_session()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = cached_session.get("authenticated",False)

if "username" not in st.session_state:
    st.session_state.username = cached_session.get("username",None)

if "session_id" not in st.session_state:
    st.session_state.session_id = cached_session.get("session_id",None)

if "signup_success" not in st.session_state:
    st.session_state.signup_success = False

if verify_session():
    st.switch_page("pages/dashboard.py")


with st.container (border= True):
    st.markdown("<h2 style='color: #FFD700;'>Signup</h2>", unsafe_allow_html=True)
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

if st.button("← Go to Homepage"):
    st.switch_page("streamlit_.py")

        