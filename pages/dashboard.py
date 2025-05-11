import streamlit as st
import requests
import pandas as pd
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
hide_sidebar_style = """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        [data-testid="collapsedControl"] {
            display: none;
        }
        [class="st-emotion-cache-169dgwr e19011e615"] {
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
            "current_chat_history":[],
            "qna": [],
            "selected_choices": {},
            "no_of_q_attempted":0,
            "test_score_list":[],
            "avg_score":0
        }
    return st.session_state.cached_session

def update_session_cache():
    st.session_state.cached_session = {
        "authenticated":st.session_state.authenticated,
        "username":st.session_state.username,
        "session_id":st.session_state.session_id,
        "chats":st.session_state.get("chats",{}),
        "active_chat_id":st.session_state.get("active_chat_id",None),
        "current_chat_history":st.session_state.get("current_chat_history",[]),
        "qna":st.session_state.get("qna",[]),
        "selected_choices": st.session_state.get("selected_choices", {}),
        "no_of_q_attempted": st.session_state.get("no_of_q_attempted", 0),
        "test_score_list": st.session_state.get("test_score_list", []),
        "avg_score": st.session_state.get("avg_score", 0)
    }
    get_cached_session.clear()
    get_cached_session()

def verify_authentication():
    try:
        session_id = st.session_state.session_id
        if not session_id:
            return False
        cookie = {"session_id":session_id}
        response = requests.get("http://127.0.0.1:8000/validate_session",cookies=cookie)
        if response.status_code == 200:
            data = response.json()
            if data["authenticated"]:
                st.session_state.authenticated = True
                st.session_state.username = data["username"]
                update_session_cache()
                return True
        st.session_state.authenticated = False
        update_session_cache()
        return False
    except requests.exceptions.RequestException as e:
        st.error(f"Server connection error.{e}")
        return st.session_state.authenticated

cached_session = get_cached_session()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = cached_session.get("authenticated",False)

if "username" not in st.session_state:
    st.session_state.username = cached_session.get("username",None)

if "session_id" not in st.session_state:
    st.session_state.session_id = cached_session.get("session_id",None)

if "chats" not in st.session_state:
    st.session_state.chats = cached_session.get("chats",{})

if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = cached_session.get("active_chat_id",None)

if "current_chat_history" not in st.session_state:
    st.session_state.current_chat_history = cached_session.get("current_chat_history",[])

if "qna" not in st.session_state:
    st.session_state.qna = cached_session.get("qna",[])

if "selected_choices" not in st.session_state:
    st.session_state.selected_choices = cached_session.get("selected_choices",{})

if "score" not in st.session_state:
    st.session_state.score = 0

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "no_of_q_attempted" not in st.session_state:
    st.session_state.no_of_q_attempted  = cached_session.get("no_of_q_attempted",0)

if "test_score_list" not in st.session_state:
    st.session_state.test_score_list = cached_session.get("test_score_list",[])

if "avg_score" not in st.session_state:
    st.session_state.avg_score = cached_session.get("avg_score",0)

if not verify_authentication():
    st.switch_page("pages/login_.py")


def get_pdf_and_split_text(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    print(text)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 500,chunk_overlap=50)
    return text_splitter.split_text(text)

st.title("Dashboard")
st.write(f"Welcome, {st.session_state.username}!")

pdf_check_response = requests.get(f"http://127.0.0.1:8000/find_pdf_name?username={st.session_state.username}")
pdf_check_json = pdf_check_response.json()
if not pdf_check_json["bool"]:
    st.write("Let us start by uploading your resume!!")
    file = st.file_uploader(label="Upload Resume",type='pdf')
    
    if file:
        files = {"file":(file.name,file,file.type)}
        data = {"username":st.session_state.username}
        with st.spinner("Uploading and initializing vector store..."):
            
            response = requests.post(f"http://127.0.0.1:8000/upload_pdf_name?username={st.session_state.username}&pdf_name={file.name}")
            response_data = response.json()

            if response.status_code ==200:
                print(response_data["message"])
                splitted_text = get_pdf_and_split_text(file)
                if splitted_text:
                    print("Text splitted successfully")
                vector_init_request = {
                    "username":st.session_state.username,
                    "splitted_text":splitted_text
                }
                init_vectorstore_response = requests.post(f"http://127.0.0.1:8000/initialize_vectorstore",json=vector_init_request)
                if init_vectorstore_response.status_code == 200:
                    init_vectorstore_response_data = init_vectorstore_response.json()
                    print(init_vectorstore_response_data["message"])
                    st.success("PDF uploaded and vector store initialized successfully!")
                    st.rerun()
                else:
                    st.error("Failed to initialize vector store.")
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
        pdf_delete_response = requests.delete(f"http://127.0.0.1:8000/delete_pdf_name?username={st.session_state.username}")
        if pdf_delete_response.status_code == 200:
            vectorstore_delete_response = requests.delete(f"http://127.0.0.1:8000/delete_vectorstore?username={st.session_state.username}")
            vectorstore_delete_response_data = vectorstore_delete_response.json()
            if vectorstore_delete_response.status_code == 200:
                chat_delete_response = requests.delete(f"http://127.0.0.1:8000/delete_chat_list?username={st.session_state.username}")
                if chat_delete_response.status_code == 200:
                    chat_history_delete_response = requests.delete(f"http://127.0.0.1:8000/delete_complete_chat_history?username={st.session_state.username}")
                    if chat_history_delete_response.status_code == 200:
                        st.session_state.chats = {}
                        st.session_state.active_chat_id = None
                        st.session_state.current_chat_history = []
                        update_session_cache()
                
                
                        if vectorstore_delete_response_data["success"]:
                            st.success("PDF and vector store deleted successfully")
                            st.rerun()
                        else:
                            st.error("Failed to delete PDF or vector store")
        

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
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.session_id = None
        update_session_cache()
        st.cache_resource.clear()
        st.switch_page('streamlit_.py')

