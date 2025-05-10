import streamlit as st
import time 
import requests
import streamlit.components.v1 as components

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
            "no_of_q_attempted":0
        }
    return st.session_state.cached_session

def update_session_cache():
    st.session_state.cached_session = {
        "authenticated":st.session_state.authenticated,
        "username":st.session_state.username,
        "session_id":st.session_state.session_id,
        "chats":st.session_state.chats,
        "active_chat_id":st.session_state.active_chat_id,
        "current_chat_history":st.session_state.current_chat_history,
        "qna":st.session_state.qna,
        "selected_choices":st.session_state.selected_choices,
        "no_of_q_attempted":st.session_state.no_of_q_attempted
    }
    get_cached_session.clear()
    get_cached_session()

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

def verify_authentication():
    try:
        session_id = st.session_state.session_id
        if not session_id:
            return False
        
        cookie = {"session_id": session_id}
        response = requests.get("http://127.0.0.1:8000/validate_session", cookies=cookie)
        
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
        st.error(f"Server connection error: {e}")
        return st.session_state.authenticated



if not verify_authentication():
    st.switch_page("pages/login_.py")

def generate_qna():
    qna_generation_response = requests.get(f"http://127.0.0.1:8000/generate_qna?username={st.session_state.username}")
    qna_generation_response_data = qna_generation_response.json()
    st.session_state.qna = qna_generation_response_data["qna_list"]
    update_session_cache()

def submit_qna():
    st.session_state.submitted = True
    st.session_state.score = 0
    for qna_item in st.session_state.qna:
        if qna_item['answer'] == st.session_state.selected_choices[qna_item["q_no"]]:
            st.session_state.score += 1

pdf_name_check_response = requests.get(f"http://127.0.0.1:8000/find_pdf_name?username={st.session_state.username}")
if pdf_name_check_response.status_code == 200:
    pdf_name_check_response_data = pdf_name_check_response.json()
    if not pdf_name_check_response_data["bool"]:
        st.switch_page("pages/dashboard.py")

if not st.session_state.qna:
    if st.button("Generate QnA"):
        if not st.session_state.qna:
            generate_qna()

if st.session_state.qna:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("Quiz App")
    with col2:
        if st.session_state.submitted:
            st.markdown(f"### Score: {st.session_state.score}/10")

    if not st.session_state.submitted:
        with st.form(key="qna_form"):
            for qna_item in st.session_state.qna:
                st.subheader(f"Q{qna_item['q_no']}: {qna_item['question']}:")

                choice = st.radio("Select your answer:",
                    qna_item["choices"],
                    key=f"q_{qna_item['q_no']}",
                    index=None
                )
                if choice is not None:
                    st.session_state.no_of_q_attempted += 1
                    st.session_state.selected_choices[qna_item["q_no"]] = choice
                    update_session_cache()

                st.write("---")

            
            if st.form_submit_button("Submit Quiz"):
                if st.session_state.no_of_q_attempted == 10:
                    submit_qna()
                    st.rerun()
                else:
                    st.toast("Attempted all questions!",icon="🧈")
    
    else:
        for qna_item in st.session_state.qna:
            user_choice = st.session_state.selected_choices[qna_item['q_no']]
            correct = user_choice == qna_item["answer"]
        
            with st.expander(f"Q{qna_item['q_no']}: {qna_item['question']}:"):
                for choice in qna_item["choices"]:
                    if choice == qna_item['answer'] and user_choice == qna_item['answer']:
                        st.success(f"✓ {choice} (Your answer - Correct!)")
                    elif choice == qna_item['answer']:
                        st.success(f"✓ {choice} (Correct answer)")
                    elif choice == user_choice:
                        st.error(f"✗ {choice} (Your answer - Incorrect)")
                    else:
                        st.markdown(f"{choice}")
        
       
        st.session_state.qna = []
        st.session_state.selected_choices = {}
        st.session_state.no_of_q_attempted = 0
        update_session_cache()



