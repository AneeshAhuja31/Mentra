import streamlit as st
import requests

with st.container(border=True):
    st.subheader("Login")
    username = st.text_input("Enter username")
    password = st.text_input("Enter password",type="password")
    if st.button("Login"):
        request = {
            "username":username,
            "password":password
        }
        response = requests.post("http://127.0.0.1:8000/login",json=request)
        
        if response.status_code ==200:
            response_data = response.json()
            if response_data.get("result"):
                #st.write(response_data.get("message"))
                st.switch_page("pages/dashboard.py")
            else:
                st.error(response_data.get("message"))
        else:
            st.error("Failed to connect to the server. Please try again later.")
    st.write("\n")
    st.write("\n")
    
    
    st.markdown(f"Aren't a user?")
    if st.button("Signup!"):
        st.switch_page("pages/signup_.py")

    # st.markdown('<a href="http://localhost:8501/pages/signup_.py" target="_self">Go to Signup Page</a>',unsafe_allow_html=True)