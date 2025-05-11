import streamlit as st
import time 
import requests
import streamlit.components.v1 as components
import pandas as pd
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
    with st.spinner("Generating MCQ"):
        qna_generation_response = requests.get(f"http://127.0.0.1:8000/generate_qna?username={st.session_state.username}")
        qna_generation_response_data = qna_generation_response.json()
        st.session_state.qna = qna_generation_response_data["qna_list"]
        update_session_cache()
    st.rerun()

def submit_qna():
    st.session_state.submitted = True
    st.session_state.score = 0
    for qna_item in st.session_state.qna:
        if qna_item['answer'] == st.session_state.selected_choices[qna_item["q_no"]]:
            st.session_state.score += 1
    
    test_score_insert_response = requests.post(f"http://127.0.0.1:8000/insert_test_score?username={st.session_state.username}&score={st.session_state.score}")
    test_score_insert_response_data = test_score_insert_response.json()
    print(test_score_insert_response_data['message'])
    

pdf_name_check_response = requests.get(f"http://127.0.0.1:8000/find_pdf_name?username={st.session_state.username}")
if pdf_name_check_response.status_code == 200:
    pdf_name_check_response_data = pdf_name_check_response.json()
    if not pdf_name_check_response_data["bool"]:
        st.switch_page("pages/dashboard.py")

if not st.session_state.qna:
    st.title("Test History")
    test_score_list_response = requests.get(f"http://127.0.0.1:8000/get_test_score_list?username={st.session_state.username}")
    if test_score_list_response.status_code == 200:
        test_score_list_response_data = test_score_list_response.json()
        st.session_state.test_score_list = test_score_list_response_data['test_score_list']
        st.session_state.avg_score = test_score_list_response_data['average']
        
        score_range = list(range(0, 11))
        scores = [int(item['score']) for item in st.session_state.test_score_list]
        frequency = [scores.count(i) for i in score_range]
        df = pd.DataFrame({'Score': score_range, 'Frequency': frequency})
        df.set_index('Score', inplace=True)
        
        st.line_chart(df)
        if scores:
            st.write(f"Average score: {st.session_state.avg_score:.2f}")
            st.write(f"Best score: {max(scores)}")
            st.write(f"Total tests taken: {len(scores)}")
        update_session_cache()

    if st.button("Generate QnA"):
        if not st.session_state.qna:
            generate_qna()
    
else:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("Resume based MCQ")
    with col2:
        if st.session_state.submitted:
            st.markdown(f"### Score: {st.session_state.score}/10")

    if not st.session_state.submitted:
        
        for qna_item in st.session_state.qna:
            st.subheader(f"Q{qna_item['q_no']}: {qna_item['question']}:")
            q_no = qna_item['q_no']
            choices = qna_item['choices']
            idx = None
            if q_no in st.session_state.selected_choices and st.session_state.selected_choices[q_no]:
                already_selected_val = st.session_state.selected_choices[q_no]
                try:
                    idx = choices.index(already_selected_val)
                except ValueError:
                    idx = None
            choice = st.radio("Select your answer:",
                qna_item["choices"],
                key=f"q_{q_no}",
                index=idx,
            )
            if choice is not None:
                st.session_state.selected_choices[q_no] = choice
                update_session_cache()
            st.write("---")
        c1,c2 = st.columns([3,1])
        with c1:
            if st.button("Abandon Test"):
                st.session_state.qna = []
                st.session_state.selected_choices = {}
                update_session_cache()
                st.rerun()
        with c2:
            if st.button("Submit Quiz"):
                actual_attempts = len(st.session_state.selected_choices)
                update_session_cache()
                if actual_attempts == 10:
                    submit_qna()
                    st.rerun()
                else:
                    st.toast("Attempted all questions!",icon="⚠️")

    else:
        for qna_item in st.session_state.qna:
            user_choice = st.session_state.selected_choices[qna_item['q_no']]
            correct = user_choice == qna_item["answer"]
        
            with st.expander(f"Q{qna_item['q_no']}: {qna_item['question']}:",expanded=True):
                for choice in qna_item["choices"]:
                    if choice == qna_item['answer'] and user_choice == qna_item['answer']:
                        st.success(f"{choice} (Your answer - Correct!)✓")
                    elif choice == qna_item['answer']:
                        st.success(f"{choice} (Correct answer)")
                    elif choice == user_choice:
                        st.error(f"{choice} (Your answer - Incorrect)✗")
                    else:
                        st.markdown(f"{choice}")
        
        if st.session_state.score == 10:
            st.balloons()
        
       
        st.session_state.qna = []
        st.session_state.selected_choices = {}
        update_session_cache()



