import streamlit as st
import requests
import pandas as pd
from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
st.set_page_config(page_title="Dashboard",page_icon="〽️",layout="centered")

hide_default_navigation = """
    <style>
    
        [data-testid="stSidebarNav"] {
            display: none;
        }
        section[data-testid="stSidebar"] div.stButton > button {
            display: block !important;
            margin-left: auto !important;
            margin-right: auto !important;
            width: 80%;
        }
            
        [data-testid="stSidebar"] {
            min-width: 210px !important;
            max-width: 210px !important;
            width: 210px !important;
        }
            
        [data-testid="stSidebar"] > div:first-child {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    </style>
"""
st.markdown(hide_default_navigation, unsafe_allow_html=True)

@st.cache_resource
def get_cached_session():
    if "cached_session" not in st.session_state:
        st.session_state.cached_session= {
            "authenticated":False,
            "username":None,
            "session_id":None,
            "filename":None,
            "chats":{},
            "active_chat_id":None,
            "current_chat_history":[],
            "qna": [],
            "selected_choices": {},
            "test_score_list":[],
            "ats":{}
        }
    return st.session_state.cached_session

def update_session_cache():
    st.session_state.cached_session = {
        "authenticated":st.session_state.authenticated,
        "username":st.session_state.username,
        "session_id":st.session_state.session_id,
        "filename":st.session_state.filename,
        "chats":st.session_state.get("chats",{}),
        "active_chat_id":st.session_state.get("active_chat_id",None),
        "current_chat_history":st.session_state.get("current_chat_history",[]),
        "qna":st.session_state.get("qna",[]),
        "selected_choices": st.session_state.get("selected_choices", {}),
        "test_score_list": st.session_state.get("test_score_list", []),
        "ats":st.session_state.get("ats",{})
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

if "filename" not in st.session_state:
    st.session_state.filename = cached_session.get("filename",None)

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

if "test_score_list" not in st.session_state:
    st.session_state.test_score_list = cached_session.get("test_score_list",[])

if "ats" not in st.session_state:
    st.session_state.ats = cached_session.get("ats",{})

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

def logout():
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
        st.session_state.filename = None
        update_session_cache()
        st.cache_resource.clear()
        st.switch_page('streamlit_.py')

st.markdown("<h1 style='color: #FFD700;'>Dashboard</h1>", unsafe_allow_html=True)
st.write(f"Welcome, {st.session_state.username}!")

def show():
    st.markdown(
        f"""
        <div style="
            border: 1px solid rgba(255, 255, 255, 0.2); 
            border-radius: 12px; 
            padding: 20px; 
            width: 100%; 
            max-width: 450px;
            background-color: rgba(45, 45, 45, 0.95);
            color: #FFFFFF;
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
            margin-bottom: 25px;
            font-family: sans-serif;
            display: flex;
            align-items: center;
        ">
            <div style="
                width: 40px;
                height: 40px;
                background-color: #FFD700;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 15px;
            ">
                <span style="font-size: 20px;">📄</span>
            </div>
            <div style="flex-grow: 1;">
                <div style="font-size: 14px; color: #AAAAAA; margin-bottom: 5px;">UPLOADED FILE</div>
                <div style="font-size: 18px; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{st.session_state.filename}</div>
            </div>
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
                        st.session_state.filename = None
                        st.session_state.ats = {}
                        update_session_cache()
                
                
                        if vectorstore_delete_response_data["success"]:
                            st.success("PDF and vector store deleted successfully")
                            st.rerun()
                        else:
                            st.error("Failed to delete PDF or vector store")

    if 'ats' in st.session_state and st.session_state.ats:
        with st.container():
            
            cols = st.columns([1, 2, 1])
            with cols[1]:
                score = st.session_state.ats.get('ats_score', 0)
                
                # Determine color based on score range
                if score >= 80:
                    color = "#006400"  # Dark Green
                elif score >= 60:
                    color = "#4CAF50"  # Green
                elif score >= 40:
                    color = "#FFC107"  # Yellow
                elif score >= 20:
                    color = "#F44336"  # Red
                else:
                    color = "#8B0000"  # Dark Red
                
                # Create circular progress bar with HTML/CSS
                html_code = f"""
                <div style="display: flex; justify-content: center; margin: 20px 0;">
                    <div style="
                        position: relative;
                        width: 180px;
                        height: 180px;
                        border-radius: 50%;
                        background: conic-gradient({color} {score}%, #333333 {score}%);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    ">
                        <div style="
                            width: 150px;
                            height: 150px;
                            background: #1E1E1E;
                            border-radius: 50%;
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                            justify-content: center;
                        ">
                            <div style="
                                font-size: 36px;
                                font-weight: bold;
                                color: {color};
                            ">{score}</div>
                            <div style="color: #AAAAAA; font-size: 14px;">out of 100</div>
                        </div>
                    </div>
                </div>
                """
                st.markdown(html_code, unsafe_allow_html=True)
                
                st.markdown(f"<h3 style='text-align: center; color: {color};'>Review</h3>", unsafe_allow_html=True)
                
                # Display review in a styled container
                review_text = st.session_state.ats.get('ats_review')
                
                st.markdown(f"""
                <div style="
                    background-color: rgba(45, 45, 45, 0.6);
                    border-radius: 10px;
                    padding: 15px;
                    margin: 10px 0;
                    border-left: 5px solid {color};
                    font-size: 16px;
                    font-style: italic;
                    line-height: 1.5;
                ">
                    \"{review_text}\"
                </div>
                """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("""
            <style>
            /* Target only buttons in the sidebar */
            section[data-testid="stSidebar"] div.stButton > button {
                display: block !important;
                margin-left: auto !important;
                margin-right: auto !important;
                width: 80%;
            }
            </style>
        """, unsafe_allow_html=True)

        if st.button("〽️entra"):
            st.switch_page("pages/dashboard.py")
    
        st.write(" ")

        if st.button("Start QnA"):
            st.switch_page("pages/qna.py")

        st.write(" ")

        if st.button("AI Helper"):
            st.switch_page("pages/ai_helper.py")

        st.write(" ")

        if st.button("Logout"):
            logout()
        
        st.write(" ")

if not st.session_state.filename:
    pdf_check_response = requests.get(f"http://127.0.0.1:8000/find_pdf_name?username={st.session_state.username}")
    pdf_check_json = pdf_check_response.json()

    # if pdf_check_json["bool"]:
    #     st.session_state.filename = pdf_check_json["filename"]
    if not pdf_check_json["bool"]:
        st.session_state.filename = None
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
                        
                        ats_generate_response = requests.get(f"http://127.0.0.1:8000/generate_ats?username={st.session_state.username}")
                        st.session_state.ats = ats_generate_response.json()
                        update_session_cache()
                        st.success("PDF uploaded and vector store initialized successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to initialize vector store.")
                else:
                    st.error(response_data.get("message"))

        with st.sidebar:
            st.markdown("""
                <style>
                section[data-testid="stSidebar"] div.stButton > button {
                    display: block !important;
                    margin-left: auto !important;
                    margin-right: auto !important;
                    width: 80%;
                }
                </style>
            """, unsafe_allow_html=True)

            if st.button("〽️entra"):
                st.switch_page("pages/dashboard.py")

            st.write(" ")

            if st.button("Start QnA"):
                st.toast("Upload file to use application features!",icon="〽️")

            st.write(" ")

            if st.button("AI Helper"):
                st.toast("Upload file to use application features!",icon="〽️")

            st.write(" ")

            if st.button("Logout"):
                logout()
    else: 
        st.session_state.filename = pdf_check_json["filename"]
        update_session_cache()
        st.rerun()
else: 
    show()
