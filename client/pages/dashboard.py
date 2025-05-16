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
            min-width: 250px !important;
            max-width: 250px !important;
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
        response = requests.get("https://mentra-backend.onrender.com/validate_session",cookies=cookie)
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


def get_pdf_text(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def logout():
    session_id = st.session_state.session_id
    cookie = {"session_id":session_id}
    response = requests.get("https://mentra-backend.onrender.com/logout",cookies=cookie)
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
    with st.container(border=True):
        st.markdown(
                f"""
                <div style="
                    border: 1px solid rgba(255, 255, 255, 0.2); 
                    border-radius: 12px; 
                    padding: 20px; 
                    width: 100%; 
                    max-width: 650px;
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
                        min-width: 40px;
                        background-color: #FFD700;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-right: 15px;
                    ">
                        <span style="font-size: 20px;">📄</span>
                    </div>
                    <div style="
                        flex-grow: 1;
                        overflow: hidden;
                        width: calc(100% - 55px);
                    ">
                        <div style="font-size: 14px; color: #AAAAAA; margin-bottom: 5px;">UPLOADED FILE</div>
                        <div style="
                            font-size: 18px; 
                            font-weight: bold; 
                            white-space: nowrap; 
                            overflow: hidden; 
                            text-overflow: ellipsis;
                            width: 100%;
                        ">{st.session_state.filename}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        col = st.columns([1,3])
        with col[0]:
            if st.button("Remove PDF"):
            
                pdf_delete_response = requests.delete(f"https://mentra-backend.onrender.com/delete_pdf_name_and_ats?username={st.session_state.username}")
                if pdf_delete_response.status_code == 200:
                    pdf_delete_response_data = pdf_delete_response.json()
                    print(pdf_delete_response_data["message"])
                    pdf_content_delete_response = requests.delete(f"https://mentra-backend.onrender.com/delete_pdf_content?username={st.session_state.username}")
                    if pdf_content_delete_response.status_code == 200:
                        pdf_content_delete_response_data = pdf_content_delete_response.json()
                        print(pdf_content_delete_response_data["message"])
                        chat_delete_response = requests.delete(f"https://mentra-backend.onrender.com/delete_chat_list?username={st.session_state.username}")
                        if chat_delete_response.status_code == 200:
                            chat_history_delete_response = requests.delete(f"https://mentra-backend.onrender.com/delete_complete_chat_history?username={st.session_state.username}")
                            if chat_history_delete_response.status_code == 200:
                                chat_history_delete_response_data = chat_history_delete_response.json()
                                print(chat_history_delete_response_data["message"])
                                questions_delete_response = requests.delete(f"https://mentra-backend.onrender.com/delete_questions?username={st.session_state.username}")
                                if questions_delete_response.status_code == 200:
                                    questions_delete_response_data = questions_delete_response.json()
                                    print(questions_delete_response_data["message"])    
                                    test_score_delete_response = requests.delete(f"https://mentra-backend.onrender.com/delete_test_scores?username={st.session_state.username}")
                                    if test_score_delete_response.status_code == 200:
                                        test_score_delete_response_data = test_score_delete_response.json()
                                        print(test_score_delete_response_data["message"])
                                    
                                    st.session_state.chats = {}
                                    st.session_state.active_chat_id = None
                                    st.session_state.current_chat_history = []
                                    st.session_state.filename = None
                                    st.session_state.ats = {}
                                    update_session_cache()
                        
                        
                                if pdf_content_delete_response_data["deleted"]:
                                    st.success("PDF deleted successfully")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete PDF")
        with col[1]:
            st.caption("Removing your PDF will also delete ALL your data on Mentra!")
    if 'ats' in st.session_state and st.session_state.ats:
        
        cols = st.columns([1,1.5])
        with cols[0]:
            with st.container(border=True):

                score = st.session_state.ats.get('ats_score', 0)
                
                if score >= 80:
                    color = "#006400"  
                elif score >= 60:
                    color = "#4CAF50"  
                elif score >= 40:
                    color = "#FFC107"  
                elif score >= 20:
                    color = "#F44336"  
                else:
                    color = "#8B0000"  

                st.markdown(f"<h3 style='text-align: center; color: {color};'>Resume Score</h3>", unsafe_allow_html=True)
                #progress bar
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
                
            
            bookmarked_chats_response = requests.get(f"https://mentra-backend.onrender.com/find_bookmarks?username={st.session_state.username}")
            bookmarked_chats_response_data = bookmarked_chats_response.json()
            bookmarked_chat_list = bookmarked_chats_response_data["bookmarked_chats_list"]
            
            with st.expander(f"{st.session_state.username}'s Bookmarks 🔖",expanded=True):
                if bookmarked_chats_response_data["bool"]:
                    for chat in bookmarked_chat_list:
                        title = chat.get("title","Untitled Chat")
                        updated_at = chat["updated_at"]
                        chat_id = chat["chat_id"]


                        with st.container():
                            col1, col2 = st.columns([4, 1])
                            
                            with col1:
                                st.markdown(f"""
                                <div style="
                                    background-color: rgba(45, 45, 45, 0.4);
                                    border-radius: 8px;
                                    padding: 10px;
                                    margin: 5px 0;
                                    border-left: 3px solid #FFD700;
                                ">
                                    <p style="font-weight: bold; margin-bottom: 5px;">{title}</p>
                                    <p style="font-size: 0.8em; color: #AAAAAA;">Updated at: {updated_at}</p>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col2:
                                st.markdown("""
                                <style>
                                /* Adjust button container vertical alignment */
                                div.stButton > button {
                                    margin-top: 13px !important;
                                }
                                </style>
                                """, unsafe_allow_html=True)
                                if st.button("→", key=f"goto_{chat_id}"):
                                    st.session_state.active_chat_id = chat_id
                                    update_session_cache()
                                    st.switch_page("pages/ai_helper.py")
                else:
                    st.info("No bookmarks Found!")
            
        with cols[1]:
            with st.container(border=True):
                st.markdown(f"<h3 style='text-align: center; color: {color};'>Review</h3>", unsafe_allow_html=True)
                
                review_text = st.session_state.ats.get('ats_review')
                
                st.markdown(f"""
                    <div style="
                        background-color: rgba(45, 45, 45, 0.6);
                        border-radius: 10px;
                        padding: 8px;
                        margin: 8px 0;
                        border-left: 5px solid {color};
                        font-size: 15px;
                        font-style: italic;
                        line-height: 1.4;
                        min-width: 350px;
                        max-width: 500px;
                        width: 90%;
                        transition: transform 0.2s cubic-bezier(.4,2,.6,1), box-shadow 0.2s;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
                    "
                    onmouseover="this.style.transform='scale(1.05)';this.style.boxShadow='0 8px 24px rgba(0,0,0,0.18)';"
                    onmouseout="this.style.transform='scale(1)';this.style.boxShadow='0 2px 8px rgba(0,0,0,0.08)';"
                    >
                        "{review_text}"
                    </div>
                    """, unsafe_allow_html=True)
                    
                    

    else:
        print("No ATS?")
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

        if st.button("📄Start QnA"):
            st.switch_page("pages/qna.py")

        st.write(" ")

        if st.button("🤖AI Mentor"):
            st.switch_page("pages/ai_helper.py")

        st.write(" ")

        #####################
        if st.button("📨Build CL"):
            st.switch_page("pages/cl_.py")
        ######################
        st.write(" ")

        if st.button("⏻Logout"):
            logout()
        
        st.write(" ")

if not st.session_state.filename:
    pdf_check_response = requests.get(f"https://mentra-backend.onrender.com/find_pdf_name?username={st.session_state.username}")
    pdf_check_json = pdf_check_response.json()

    if not pdf_check_json["bool"]:
        st.session_state.filename = None
        st.write("Let us start by uploading your resume!!")
        file = st.file_uploader(label="Upload Resume",type='pdf')
        
        if file:
            files = {"file":(file.name,file,file.type)}
            data = {"username":st.session_state.username}
            with st.spinner("Uploading pdf and generating ATS..."):
                
                pdf_text = get_pdf_text(file)
                if len(PdfReader(file).pages) > 2:  # Example: max 10 pages
                    st.error("Resume exceeds maximum page limit.")
                    st.stop()
                pdf_upload_request = {
                    "username":st.session_state.username,
                    "pdf_content":pdf_text
                }
                pdf_upload_response = requests.post(f"https://mentra-backend.onrender.com/upload_pdf_content",json=pdf_upload_request)
                if pdf_upload_response.status_code == 200:
                    pdf_upload_response_data = pdf_upload_response.json()
                    print(pdf_upload_response_data["message"])

                    pdf_name_upload_response = requests.post(f"https://mentra-backend.onrender.com/upload_pdf_name?username={st.session_state.username}&pdf_name={file.name}")
                    if pdf_name_upload_response.status_code == 200:
                        pdf_name_upload_response_data = pdf_name_upload_response.json()
                        print(pdf_name_upload_response_data["message"])
                    
                        if not st.session_state.ats:
                            ats_generate_response = requests.get(f"https://mentra-backend.onrender.com/generate_ats?username={st.session_state.username}")
                            st.session_state.ats = ats_generate_response.json()
                            insert_ats_body = {
                                "username":st.session_state.username,
                                "ats_score":st.session_state.ats["ats_score"],
                                "ats_review":st.session_state.ats["ats_review"]
                            }
                            
                            ats_insert_response = requests.post(f"https://mentra-backend.onrender.com/insert_ats",json=insert_ats_body)
                            if ats_insert_response.status_code == 200:
                                ats_insert_response_data = ats_insert_response.json()
                                print(ats_insert_response_data["message"])

                                questions_init_response = requests.post(f"https://mentra-backend.onrender.com/init_questions?username={st.session_state.username}")
                                if questions_init_response.status_code == 200:
                                    questions_init_response_data = questions_init_response.json()
                                    print(questions_init_response_data["message"])
                            

                        update_session_cache()
                        st.success("PDF uploaded successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to upload pdf.")
                else:
                    pdf_upload_response_data = pdf_upload_response.json()
                    st.error(pdf_upload_response_data["message"])

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

            if st.button("📄Start QnA"):
                st.toast("Upload file to use application features!",icon="〽️")

            st.write(" ")

            if st.button("🤖AI Mentor"):
                st.toast("Upload file to use application features!",icon="〽️")

            st.write(" ")

            if st.button("📨Build CL"):
                st.toast("Upload file to use application features!",icon="〽️")
        
            st.write(" ")

            if st.button("⏻Logout"):
                logout()
    else: 
        st.session_state.filename = pdf_check_json["filename"]
        if not st.session_state.ats:
            ats_find_response = requests.get(f"https://mentra-backend.onrender.com/find_ats?username={st.session_state.username}")
            if ats_find_response.status_code == 200:
                ats_find_response_data = ats_find_response.json()
                if ats_find_response_data["bool"]:
                    st.session_state.ats = {
                        "ats_score":ats_find_response_data["ats_score"],
                        "ats_review":ats_find_response_data["review"]
                    }
        update_session_cache()
        st.rerun()
else:  #if we have filename but not ats, get ats from db   
    if not st.session_state.ats:
        ats_find_response = requests.get(f"https://mentra-backend.onrender.com/find_ats?username={st.session_state.username}")
        if ats_find_response.status_code == 200:
            ats_find_response_data = ats_find_response.json()
            if ats_find_response_data["bool"]:
                st.session_state.ats = {
                    "ats_score":ats_find_response_data["ats_score"],
                    "ats_review":ats_find_response_data["review"]
                }
                update_session_cache()
                st.rerun()
    show()
