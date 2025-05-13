import streamlit as st
import time 
import requests
import streamlit.components.v1 as components
import uuid
import asyncio
st.set_page_config(page_title="AI Mentor",page_icon="〽️",layout="centered")

hide_default_navigation = """
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
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
            "input_disabled":False
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
        "input_disabled":st.session_state.input_disabled
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

if "input_disabled" not in st.session_state:
    st.session_state.input_disabled = cached_session.get("input_disabled",False)

if "message_to_process" not in st.session_state:
    st.session_state.message_to_process = cached_session.get("message_to_process",None)

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
        response = requests.get("https://mentra-wtcc.onrender.com/validate_session", cookies=cookie)
        
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


pdf_name_check_response = requests.get(f"https://mentra-wtcc.onrender.com/find_pdf_name?username={st.session_state.username}")
if pdf_name_check_response.status_code == 200:
    pdf_name_check_response_data = pdf_name_check_response.json()
    if not pdf_name_check_response_data["bool"]:
        st.switch_page("pages/dashboard.py")

chat_list_response = requests.get(f"https://mentra-wtcc.onrender.com/get_chat_list?username={st.session_state.username}")
if chat_list_response.status_code == 200:
    chats_list_response_json = chat_list_response.json()
    chats_data = chats_list_response_json["chat_list"]
    for chat in chats_data:
        st.session_state.chats[chat["chat_id"]] = {
            "title":chat["title"],
            "bookmarked":chat["bookmarked"]
        }

    if st.session_state.chats and not st.session_state.active_chat_id:
        st.session_state.active_chat_id = next(iter(st.session_state.chats))

    if st.session_state.active_chat_id:
        chat_history_response = requests.get(f"https://mentra-wtcc.onrender.com/get_chat_history_for_ui?chat_id={st.session_state.active_chat_id}")
        if chat_history_response.status_code == 200:
            st.session_state.current_chat_history = chat_history_response.json()
    
    update_session_cache()



def insert_component(chat_id):
    components.html(f"""
    <script>
        localStorage.setItem("chat_id", {chat_id});
    </script>
    """, height=0)
    

def create_new_chat(title):
    chat_id = f"{st.session_state.username}_chat_{uuid.uuid4()}"
    insert_component(chat_id)
    response = requests.post(f"https://mentra-wtcc.onrender.com/new_chat?chat_id={chat_id}&username={st.session_state.username}&title={title}")
    if response.status_code == 200:
        response_data = response.json()
        msg = response_data["message"]
        print(f"{msg}")
        st.session_state.chats[chat_id] = {
            "title":title
        }
        st.session_state.active_chat_id = chat_id
        st.session_state.current_chat_history = []
        st.session_state.input_disabled = False
        update_session_cache()
        st.rerun()

def select_chat(chat_id):
    st.session_state.active_chat_id = chat_id
    insert_component(chat_id)
    st.session_state.input_disabled = False
    response = requests.get(f"https://mentra-wtcc.onrender.com/get_chat_history_for_ui?chat_id={chat_id}")
    if response.status_code == 200:
        response_data = response.json()
        st.session_state.current_chat_history = response_data
    update_session_cache()
    st.rerun()

def delete_chat(chat_id):
    response = requests.delete(f"https://mentra-wtcc.onrender.com/delete_chat?chat_id={chat_id}")
    if response.status_code == 200:
        response_data = response.json()
        print(response_data["message"])
        if chat_id in st.session_state.chats:
            del st.session_state.chats[chat_id]
        
        delete_chat_history_response = requests.delete(f"https://mentra-wtcc.onrender.com/delete_chat_history_by_chat_id?chat_id={chat_id}")
        if delete_chat_history_response.status_code == 200:
            delete_chat_history_response_data = delete_chat_history_response.json()
            print(delete_chat_history_response_data["message"])
        
        if chat_id == st.session_state.active_chat_id:
            if st.session_state.chats:
                new_active_chat = next(iter(st.session_state.chats))
                st.session_state.active_chat_id = new_active_chat
                chathistory_for_ui_response = requests.get(f"https://mentra-wtcc.onrender.com/get_chat_history_for_ui?chat_id={new_active_chat}")
                if chathistory_for_ui_response.status_code == 200:
                    st.session_state.current_chat_history = chathistory_for_ui_response.json()
                else:
                    st.session_state.current_chat_history = []
            else:
                st.session_state.active_chat_id = None
                st.session_state.current_chat_history = []
        
        update_session_cache()
        st.rerun()

def bookmark_chat(chat_id):
    current_bookmark_status = st.session_state.chats[chat_id].get("bookmarked", False)
    
    if not current_bookmark_status:
        current_bookmark_count = sum(1 for _, chat_info in st.session_state.chats.items() 
                                   if chat_info.get("bookmarked", False))
        
        if current_bookmark_count >= 5:
            st.toast("Max limit of 5 bookmarks reached!",icon="〽️")
            return
        bookmark_response = requests.post(f"https://mentra-wtcc.onrender.com/bookmark_chat?chat_id={chat_id}")
        if bookmark_response.status_code == 200:
            bookmark_response_data = bookmark_response.json()
            if bookmark_response_data["updated"]:
                st.session_state.chats[chat_id]["bookmarked"] = True
                
    else:
        unbookmark_response = requests.post(f"https://mentra-wtcc.onrender.com/unbookmark_chat?chat_id={chat_id}")
        if unbookmark_response.status_code == 200:
            unbookmark_response_data = unbookmark_response.json()
            if unbookmark_response_data["updated"]:
                st.session_state.chats[chat_id]["bookmarked"] = False
    
    update_session_cache()
    st.rerun()

with st.sidebar:
    if st.button("〽️entra"):
            st.switch_page("pages/dashboard.py")
    st.write(" ")
    st.markdown("<h1 style='color: #FFD700;'>Your Chats</h1>", unsafe_allow_html=True)
    if "show_title_input" not in st.session_state:
        st.session_state.show_title_input = False
    
    if not st.session_state.show_title_input:
        if st.button("+ New Chat"):
            st.session_state.show_title_input = True
            st.rerun()
    else:
        with st.container():
            chat_title = st.text_input("Enter chat title:", key="new_chat_title")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Create"):
                    if chat_title:
                        create_new_chat(chat_title)
                    else:
                        create_new_chat("New Chat")
                    st.session_state.show_title_input = False
            with col2:
                if st.button("Cancel"):
                    st.session_state.show_title_input = False
                    st.rerun()
    st.divider()
    if st.session_state.chats:
        for chat_id,chat_info in st.session_state.chats.items():
            col1,col2,col3 = st.columns([3,1,1])
            with col1:
                is_active = chat_id == st.session_state.active_chat_id
                button_style = "primary" if is_active else "secondary"
                if st.button(chat_info['title'],key=chat_id,use_container_width=True,type=button_style):
                    select_chat(chat_id)
            with col2:
                if st.button("🗑",key=f"delete_{chat_id}"):
                    delete_chat(chat_id)
            with col3:
                is_bookmarked = st.session_state.chats[chat_id].get("bookmarked",False) 
                button_icon = "🔖" if is_bookmarked else "📌"
                if st.button(button_icon,key=f"bookmark_{chat_id}"):
                    
                    bookmark_chat(chat_id)

def response_generator(text):
    paragraphs = text.split("\n")
    for i,paragraph in enumerate(paragraphs):
        if paragraph:
            words = paragraph.split(" ")
            for word in words:
                yield word + " "
                time.sleep(0.02)
            
            if i < len(paragraphs) - 1:
                yield "\n"

async def process_message(chat_id,prompt):
    doc = {
        "chat_id":chat_id,
        "content":prompt,
        "username":st.session_state.username
    }
    response = requests.post(f"https://mentra-wtcc.onrender.com/process_message",json=doc)
    if response.status_code == 200:
        response_data = response.json()
        return response_data['response']
    else:
        return "Sorry, I encountered an error processing your request"

if st.session_state.active_chat_id and st.session_state.active_chat_id in st.session_state.chats:
    if not st.session_state.message_to_process:
        st.session_state.input_disabled = False
      
    title = st.session_state.chats[st.session_state.active_chat_id]["title"]
    st.markdown(f"<h1 style='color: #FFD700;'>Chat: {title}</h1>", unsafe_allow_html=True)


    if st.session_state.current_chat_history:
        for chat_info in st.session_state.current_chat_history:
            if chat_info["role"] == "human":
                st.chat_message("user").markdown(chat_info["content"])
            elif chat_info["role"] == "ai":
                st.chat_message("assistant").markdown(chat_info["content"])
    
    if st.session_state.message_to_process:
        prompt = st.session_state.message_to_process
        st.chat_message("user").markdown(prompt)
        st.session_state.message_to_process = None
        input_placeholder = st.empty()
        with st.spinner("Thinking..."):
            response_text = asyncio.run(process_message(st.session_state.active_chat_id,prompt))
        st.session_state.current_chat_history.append({
            "role":"ai",
            "content":response_text
        })
        st.session_state.input_disabled = False

        update_session_cache()
        st.chat_message("assistant").write_stream(response_generator(response_text))
        st.rerun()
            
    input_container = st.container()
    with input_container:
        if not st.session_state.input_disabled:
            if prompt := st.chat_input("Type your message...",disabled=st.session_state.input_disabled):
                st.session_state.current_chat_history.append({
                    "role":"human",
                    "content":prompt
                })
                st.session_state.input_disabled = True
                st.session_state.message_to_process = prompt
                update_session_cache()
                st.rerun()
        
        else:
            st.markdown("""
            <div style="background-color:#f0f2f6; border-radius:8px; padding:10px; margin-top:10px;">
                <span style="color:#7e7e7e;">Processing message... please wait</span>
            </div>
            """, unsafe_allow_html=True)

else:
    st.info("Create a new chat to get started!")



