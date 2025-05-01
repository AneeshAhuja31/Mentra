import requests.cookies
import streamlit as st
import requests
from http.cookies import SimpleCookie


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

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

with st.container(border=True):
    st.subheader("Login")
    username = st.text_input("Enter username")
    password = st.text_input("Enter password",type="password")
    if st.button("Login"):
        request = {
            "username":username,
            "password":password
        }
        # Setting up session to preserve cookies
        response = st.session_state.requests_session.post("http://127.0.0.1:8000/login",json=request)
        response_data = response.json()
        if response.status_code ==200 and response_data.get('result') == True:
            cookie_header = response.headers['set-cookie']
            cookie = SimpleCookie()
            cookie.load(cookie_header)
            session_id = cookie['session_id'].value
            st.session_state.session_id = session_id
            st.session_state.authenticated = True
            st.session_state.username = response_data.get("username")
            st.rerun()
        else:
            st.error(response_data.get("message"))
    st.write("\n")
    st.write("\n")
    
    
    st.markdown(f"Aren't a user?")
    if st.button("Signup!"):
        st.switch_page("pages/signup_.py")

    # st.markdown('<a href="http://localhost:8501/pages/signup_.py" target="_self">Go to Signup Page</a>',unsafe_allow_html=True)