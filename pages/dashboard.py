import streamlit as st
import requests

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    session_id = st.session_state.get("session_id",None)
    if session_id:
        cookie = {"session_id":session_id}
        response = requests.get("http://127.0.0.1:8000/validate_session",cookies=cookie)
        if response.status_code == 200:
            data = response.json()
            if data['authenticated']:
                st.session_state.authenticated = True
                st.session_state.username = data["username"]
            else:
                st.switch_page("pages/login_.py")
        else:
            st.switch_page("pages/login_.py")
    else:
        st.switch_page("pages/login_.py")

st.write("Dashboard")
st.write(f"Welcome, {st.session_state.username}!")

if st.button("Logout"):
    session_id = st.session_state.session_id
    cookie = {"session_id":session_id}
    response = requests.get("http://127.0.0.1:8000/logout",cookies=cookie)
    response_data = response.json()
    if response_data.get('result'):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.session_id = None
        st.switch_page('streamlit_.py')