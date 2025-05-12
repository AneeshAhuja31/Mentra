import requests.cookies
import streamlit as st
import requests
from http.cookies import SimpleCookie
st.set_page_config(page_title="Login",page_icon="〽️",layout="centered")

hide_sidebar_style = """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        [data-testid="collapsedControl"] {
            display: none;
        }
        [data-testid ="stSidebarCollapsedControl"] {
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
            "current_chat_history": []
        }
    return st.session_state.cached_session

def update_session_cache():
    st.session_state.cached_session = {
        "authenticated":st.session_state.authenticated,
        "username":st.session_state.username,
        "session_id":st.session_state.session_id,
        "chats": st.session_state.get("chats", {}),
        "active_chat_id": st.session_state.get("active_chat_id", None),
        "current_chat_history": st.session_state.get("current_chat_history", [])
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
            response = requests.get("http://127.0.0.1:8000/validate_session", cookies=cookie)

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
    st.session_state.authenticated = False

if "username" not in st.session_state:
    st.session_state.username = cached_session.get("username",None)

if "session_id" not in st.session_state:
    st.session_state.session_id = cached_session.get("session_id",None)

if verify_session():
    st.switch_page("pages/dashboard.py")

with st.container(border=True):
    st.markdown("<h2 style='color: #FFD700;'>Login</h2>", unsafe_allow_html=True)
    username = st.text_input("Enter username")
    password = st.text_input("Enter password",type="password")
    if st.button("Login"):
        with st.spinner("Logging in..."):
            request = {
                "username":username,
                "password":password
            }
            try:
                response = requests.post("http://127.0.0.1:8000/login",json=request)
                response_data = response.json()
                if response.status_code == 200 and response_data.get('result') == True:
                    cookie_header = response.headers['set-cookie']
                    cookie = SimpleCookie()
                    cookie.load(cookie_header)
                    if "session_id" in cookie:
                        session_id = cookie['session_id'].value
                        st.session_state.session_id = session_id
                        st.session_state.authenticated = True
                        st.session_state.username = response_data.get("username")
                        update_session_cache()
                        st.success("Login successful!")
                        st.rerun()
                else:
                    st.error(response_data.get("message"))
            except Exception as e:
                st.error(f"Connection error: {str(e)}")

    st.write("\n")
    st.write("\n")
    
    st.markdown(f"Aren't a user?")
    if st.button("Signup!"):
        st.switch_page("pages/signup_.py")

if st.button("← Go to Homepage"):
    st.switch_page("streamlit_.py")