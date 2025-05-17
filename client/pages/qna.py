import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="QnA",page_icon="〽️",layout="centered")


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
            "ats":{},
        }
    return st.session_state.cached_session

def update_session_cache():
    st.session_state.cached_session = {
        "authenticated":st.session_state.authenticated,
        "username":st.session_state.username,
        "session_id":st.session_state.session_id,
        "filename":st.session_state.filename,
        "chats":st.session_state.chats,
        "active_chat_id":st.session_state.active_chat_id,
        "current_chat_history":st.session_state.current_chat_history,
        "qna":st.session_state.qna,
        "selected_choices":st.session_state.selected_choices,
        "test_score_list":st.session_state.test_score_list,
        "ats":st.session_state.ats, 
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

if "test_score_list" not in st.session_state:
    st.session_state.test_score_list = cached_session.get("test_score_list",[])

if "ats" not in st.session_state:
    st.session_state.ats = cached_session.get("ats",{})

if "submitted" not in st.session_state:
    st.session_state.submitted = False


def verify_authentication():
    try:
        session_id = st.session_state.session_id
        if not session_id:
            return False
        
        cookie = {"session_id": session_id}
        response = requests.get("https://mentra-backend.onrender.com/validate_session", cookies=cookie)
        
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

def logout():
    session_id = st.session_state.session_id
    cookie = {"session_id":session_id}
    response = requests.get("https://mentra-backend.onrender.com/logout",cookies=cookie)
    response_data = response.json()
    if response_data.get('result'):
        all_keys = list(st.session_state.keys())
        for key in all_keys:
            del st.session_state[key]
            
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.session_id = None
        st.session_state.filename = None
        st.session_state.chats = {}
        st.session_state.active_chat_id = None  
        st.session_state.current_chat_history = []
        st.session_state.qna = []
        st.session_state.selected_choices = {}
        st.session_state.test_score_list = []
        st.session_state.submitted = False
        st.session_state.ats = {}
        
        update_session_cache()
        st.cache_resource.clear()
        st.switch_page('streamlit_.py')

def generate_qna():
    st.session_state.qna = []
    st.session_state.selected_choices = {}
    st.session_state.submitted = False
    update_session_cache()
    with st.spinner("Generating MCQ. This may take some time...."):
        qna_generation_response = requests.get(f"https://mentra-backend.onrender.com/generate_qna?username={st.session_state.username}")
        qna_generation_response_data = qna_generation_response.json()
        st.session_state.qna = qna_generation_response_data["qna_list"]
        update_session_cache()
    st.rerun()

def submit_qna():
    st.session_state.submitted = True
    st.session_state.score = 0
    wrong_questions = []
    right_questions = []

    for qna_item in st.session_state.qna:
        if qna_item['answer'] == st.session_state.selected_choices[qna_item["q_no"]]:
            st.session_state.score += 1
            right_questions.append(qna_item["question"])
        else:
            wrong_questions.append(qna_item["question"])
    
    test_score_insert_response = requests.post(f"https://mentra-backend.onrender.com/insert_test_score?username={st.session_state.username}&score={st.session_state.score}")
    if test_score_insert_response.status_code == 200:
        test_score_insert_response_data = test_score_insert_response.json()
        print(test_score_insert_response_data['message'])

    questions_update_body = {
        "username":st.session_state.username,
        "wrong_questions":wrong_questions,
        "right_questions":right_questions
    }

    questions_update_response = requests.put("https://mentra-backend.onrender.com/update_questions",json=questions_update_body)
    if questions_update_response.status_code == 200:
        questions_update_response_data = questions_update_response.json()
        print(questions_update_response_data["message"])
    

pdf_name_check_response = requests.get(f"https://mentra-backend.onrender.com/find_pdf_name?username={st.session_state.username}")
if pdf_name_check_response.status_code == 200:
    pdf_name_check_response_data = pdf_name_check_response.json()
    if not pdf_name_check_response_data["bool"]:
        st.switch_page("pages/dashboard.py")

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

        if st.button("🤖AI Helper"):
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

if not st.session_state.qna:
    st.markdown("<h1 style='color: #FFD700;'>Test History</h1>", unsafe_allow_html=True)
    test_score_list_response = requests.get(f"https://mentra-backend.onrender.com/get_test_score_list?username={st.session_state.username}")
    if test_score_list_response.status_code == 200:
        test_score_list_response_data = test_score_list_response.json()
        st.session_state.test_score_list = test_score_list_response_data['test_score_list']
        
        score_range = list(range(0, 11))
        scores = [int(item['score']) for item in st.session_state.test_score_list]
        frequency = [scores.count(i) for i in score_range]
        df = pd.DataFrame({'Score': score_range, 'Frequency': frequency})
        df.set_index('Score', inplace=True)
        
        st.markdown("### Score Distribution")
        chart_container = st.container(border=True)
        with chart_container:
            st.line_chart(
                df, 
                color="#FFD700", 
                use_container_width=True
            )
        
        if scores:
            stats_container = st.container(border=True)
            with stats_container:
                st.markdown("### Performance Metrics")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="Average Score", 
                        value=f"{(sum(scores)/len(scores)):.1f}/10",
                        help="Your average performance across all tests"
                    )
                    
                with col2:
                    st.metric(
                        label="Best Score", 
                        value=f"{max(scores)}/10",
                        delta=f"+{max(scores) - (sum(scores)/len(scores)):.1f}" if max(scores) > sum(scores)/len(scores) else None,
                        help="Your highest achieved score"
                    )
                    
                with col3:
                    st.metric(
                        label="Tests Completed", 
                        value=f"{len(scores)}",
                        help="Total number of quizzes taken"
                    )
        update_session_cache()

    with st.container():
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown("<h3 style='color: #FFD700;'>Ready for a Quiz?</h3>", unsafe_allow_html=True)
            st.write("Test your knowledge with questions based on your resume")
        

    if st.button("Generate QnA"):
        if not st.session_state.qna:
            generate_qna()
    
else:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("<h1 style='color: #FFD700;'>Resume based test</h1>", unsafe_allow_html=True)
    with col2:
        if st.session_state.submitted:
            st.markdown(f"### Score: {st.session_state.score}/10")

    if not st.session_state.submitted:
        
        for qna_item in st.session_state.qna:
            st.markdown(f"<h3 style='color: #FFD700;'>Q{qna_item['q_no']}: {qna_item['question']}:</h3>", unsafe_allow_html=True)
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
                    st.toast("Attempt all questions!",icon="⚠️")

    else:
        for qna_item in st.session_state.qna:
            user_choice = st.session_state.selected_choices.get(qna_item['q_no'],"No answer selected!")
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
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("← Back to Test History", use_container_width=True):
                st.session_state.qna = []
                st.session_state.selected_choices = {}
                st.session_state.submitted = False
                update_session_cache()
                st.rerun()
       
        st.session_state.qna = []
        st.session_state.selected_choices = {}
        update_session_cache()



