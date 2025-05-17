import streamlit as st
import time 
import requests

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

if "text" not in st.session_state:
    st.session_state.text = None


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

        if st.button("📨Build CL"):
            st.switch_page("pages/cl_.py")
        
        st.write(" ")

        if st.button("⏻Logout"):
            logout()
        
        st.write(" ")

st.markdown("<h1 style='color: #FFD700;'>Cover Letter Generator</h1>", unsafe_allow_html=True)

with st.form("cover_letter_form"):
    job_description = st.text_area("Paste the job description here:", height=200)
    
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("Company Name:")
    with col2:
        hiring_manager = st.text_input("Hiring Manager Name:", value="Hiring Manager")
    
    submit_button = st.form_submit_button("Generate Cover Letter")

    if submit_button:
        if not job_description:
            st.toast("Please provide a job description to generate a cover letter.",icon="〽️")
        elif not company_name:
            st.toast("Please provide company name to generate a cover letter.",icon="〽️")
        elif not len(job_description)>50:
            st.toast("The job description must be atleast 50 characters",icon="〽️")

        else:
            with st.spinner("Generating your cover letter..."):
                response = requests.post(
                    "https://mentra-backend.onrender.com/generate_cl",
                    json={
                        "username": st.session_state.username,
                        "job_description": job_description,
                        "hiring_manager": hiring_manager,
                        "company_name": company_name
                    }
                )
                response_data = response.json()
                st.session_state.text = response_data["text"] 

if st.session_state.text:
    
    st.code(st.session_state.text)
    st.info("Cover letter code block shown above. Copy it from there!")
    st.caption("There maybe some placeholders in your cover letter that you can fill up manually!")

    st.download_button(
        label="Download as TXT",
        data=st.session_state.text,
        file_name=f"Cover_Letter_{company_name}_{time.strftime('%Y%m%d')}.txt",
        mime="text/plain"
    )
                    
st.write(" ")
with st.expander("Cover Letter Tips"):
    st.markdown("""
    <h3 style='color: #FFD700;'>Tips for a Great Cover Letter</h3>"""
    , unsafe_allow_html=True)

    st.markdown(
    """
    1. **Customize for each job** - Tailor your cover letter to the specific position
    2. **Research the company** - Show you understand their mission and values
    3. **Highlight achievements** - Provide specific examples with measurable results
    4. **Keep it concise** - Aim for 250-350 words (one page)
    5. **Proofread carefully** - Check for grammar and spelling errors
    """
    )
