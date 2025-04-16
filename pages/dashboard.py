import streamlit as st
import requests

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    session = st.session_state.get("requests_session",requests.Session())
    response = session.get("http://127.0.0.1:8000/validate_session",cookies=requests.cookies.RequestsCookieJar())
    if response.status_code == 200:
        data = response.json()
        if data['authenticated']:
            st.session_state.authenticated = True
            st.session_state.username = data["username"]
        else:
            st.switch_page("pages/login_.py")
    else:
        st.switch_page("pages/login_.py")

st.write("Dashboard")
st.write(f"Welcome, {st.session_state.username}!")