import streamlit as st
import requests
from pypdf import PdfReader
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

#caching a session state variable 'cached_session' since session variables get lost on reloading
@st.cache_resource
def get_cached_session():
    if "cached_session" not in st.session_state:
        st.session_state.cached_session= {
            "authenticated":False,
            "username":None,
            "session_id":None
        }
    return st.session_state.cached_session

cached_session = get_cached_session()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = cached_session.get("authenticated",False)

if "username" not in st.session_state:
    st.session_state.username = cached_session.get("username",None)


if "session_id" not in st.session_state:
    st.session_state.session_id = cached_session.get("session_id",None)

def update_session_cache():
    st.session_state.cached_session = {
        "authenticated":st.session_state.authenticated,
        "username":st.session_state.username,
        "session_id":st.session_state.session_id
    }
    get_cached_session.clear()
    get_cached_session()

if not st.session_state.authenticated:
    session_id = st.session_state.get("session_id",None)
    if session_id:
        cookie = {"session_id":session_id}
        response = requests.get("http://127.0.0.1:8000/validate_session",cookies=cookie)
        if response.status_code == 200:
            data = response.json()
            if data['authenticated']:
                st.session_state.authenticated = True
                st.session_state.username = data["username"]
                update_session_cache()
            else:
                st.switch_page("pages/login_.py")
        else:
            st.switch_page("pages/login_.py")
    else:
        st.switch_page("pages/login_.py")


st.title("Dashboard")
st.write(f"Welcome, {st.session_state.username}!")

st.write("Let us start by uploading your resume!!")

pdf_check_request = {
    "username":st.session_state.username
}
pdf_check_response = requests.get(f"http://127.0.0.1:8000/find_pdf?username={st.session_state.username}")
print(f"ok ok ok---------{pdf_check_response.text}")
pdf_check_json = pdf_check_response.json()
if not pdf_check_json["bool"]:
    file = st.file_uploader(label="Upload Resume",type='pdf')
    if file:
        files = {"file":(file.name,file,file.type)}
        data = {"username":st.session_state.username}
        # request = {
        #     "file":file,
        #     "username":st.session_state.username
        # }
        response = requests.post("http://127.0.0.1:8000/upload_pdf",files=files,data=data)
        
        response_data = response.json()
        if response.status_code ==200:
            st.success(response_data.get("message"))
            st.rerun()
        else:
            st.error(response_data.get("message"))
else:
    st.markdown(
        f"""
        <div style="border: 1px solid #ccc; padding: 10px; width: 300px; height: 100px; overflow-y: auto; background-color: #f9f9f9;">
            {pdf_check_json.get("filename")}
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Remove PDF"):
        response = requests.delete(f"http://127.0.0.1:8000/delete_pdf?username={st.session_state.username}")
        st.rerun()

    if st.button("Start QnA"):
        st.switch_page("pages/qna.py")

    if st.button("Analyse"):
        st.switch_page("pages/analyse_pdf.py")

    if st.button("AI Helper"):
        st.switch_page("pages/ai_helper.py")

if st.button("Logout"):
    session_id = st.session_state.session_id
    cookie = {"session_id":session_id}
    response = requests.get("http://127.0.0.1:8000/logout",cookies=cookie)
    response_data = response.json()
    if response_data.get('result'):
        get_cached_session().clear()
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.session_id = None
        st.session_state.cached_session = {
            "authenticated":False,
            "username":None,
            "session_id":None
        }
        get_cached_session()
        st.switch_page('streamlit_.py')

