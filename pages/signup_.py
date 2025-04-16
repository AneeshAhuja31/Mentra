import streamlit as st
import requests

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
                    st.write(response_data.get("message"))
                    if st.button("Login"):
                        st.switch_pag("pages/login_.py")
                else:
                    st.error(response_data.get("message"))
        