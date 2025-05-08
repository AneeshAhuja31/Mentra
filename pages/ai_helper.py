import streamlit as st
import time 
import random
import requests
import streamlit.components.v1 as components
import uuid
import asyncio
@st.cache_resource
def get_cached_session():
    if "cached_session" not in st.session_state:
        st.session_state.cached_session= {
            "authenticated":False,
            "username":None,
            "session_id":None,
            "chats":{},
            "active_chat_id":None,
            "current_chat_history":[]
        }
    return st.session_state.cached_session

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

def update_session_cache():
    st.session_state.cached_session = {
        "authenticated":st.session_state.authenticated,
        "username":st.session_state.username,
        "session_id":st.session_state.session_id,
        "chats":st.session_state.chats,
        "active_chat_id":st.session_state.active_chat_id,
        "current_chat_history":st.session_state.current_chat_history
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

                if not st.session_state.chats:
                    response = requests.get(f"http://127.0.0.1:8000/get_chat_list?username={st.session_state.username}")
                    if response.status_code == 200:
                        chats_data = response.json()
                        for chat in chats_data:
                            st.session_state.chats[chat["chat_id"]] = {
                                "title":chat["title"]
                            }
                        update_session_cache()

                        if st.session_state.chats and not st.session_state.active_chat_id:
                            st.session_state.active_chat_id = next(iter(st.session_state.chats))
                            update_session_cache()

                        if not st.session_state.current_chat_history:
                            response = requests.get(f"http://127.0.0.1:8000/get_chat_history_for_ui?chat_id={st.session_state.active_chat_id}")
                            if response.status_code == 200:
                                response_data = response.json()
                                st.session_state.current_chat_history = response_data
                                update_session_cache()
            else:
                st.switch_page("pages/login_.py")
        else:
            st.switch_page("pages/login_.py")
    else:
        st.switch_page("pages/login_.py")

def insert_component(chat_id):
    components.html(f"""
    <script>
        localStorage.setItem("chat_id", {chat_id});
    </script>
    """, height=0)
    

def create_new_chat():
    chat_id = f"{st.session_state.username}_chat_{uuid.uuid4()}"
    time_ = time.strftime("%Y-%m-%d %H:%M:%S")
    title = f"{time_}"
    insert_component(chat_id)
    response = requests.post(f"http://127.0.0.1:8000/new_chat?chat_id={chat_id}&username={st.session_state.username}&title={title}")
    if response.status_code == 200:
        response_data = response.json()
        msg = response_data["message"]
        print(f"{msg}")
        st.session_state.chats[chat_id] = {
            "title":title
        }
        st.session_state.active_chat_id = chat_id
        st.session_state.current_chat_history = []
        update_session_cache()
        st.rerun()

def select_chat(chat_id):
    st.session_state.active_chat_id = chat_id
    insert_component(chat_id)
    response = requests.get(f"http://127.0.0.1:8000/get_chat_history_for_ui?chat_id={chat_id}")
    if response.status_code == 200:
        response_data = response.json()
        st.session_state.current_chat_history = response_data
    update_session_cache()
    st.rerun()

def delete_chat(chat_id):
    response = requests.delete(f"http://127.0.0.1:8000/delete_chat?chat_id={chat_id}")
    if response.status_code == 200:
        response_data = response.json()
        print(response_data["message"])
        if chat_id in st.session_state.chats:
            del st.session_state.chats[chat_id]
        
        delete_chat_history_response = requests.delete(f"http://127.0.0.1:8000/delete_chat_history?chat_id={chat_id}")
        if delete_chat_history_response.status_code == 200:
            delete_chat_history_response_data = delete_chat_history_response.json()
            print(delete_chat_history_response_data["message"])
        
        if chat_id == st.session_state.active_chat_id:
            if st.session_state.chats:
                new_active_chat = next(iter(st.session_state.chats))
                st.session_state.active_chat_id = new_active_chat
                chathistory_for_ui_response = requests.get(f"http://127.0.0.1:8000/get_chat_history_for_ui?chat_id={new_active_chat}")
                if chathistory_for_ui_response.status_code == 200:
                    st.session_state.current_chat_history = chathistory_for_ui_response.json()
                else:
                    st.session_state.current_chat_history = []
            else:
                st.session_state.active_chat_id = None
                st.session_state.current_chat_history = []
        
        update_session_cache()
        st.rerun()
    


with st.sidebar:
    st.title("Chat History")
    if st.button("+ New Chat"):
        create_new_chat()
    st.divider()
    if st.session_state.chats:
        for chat_id,chat_info in st.session_state.chats.items():
            col1,col2 = st.columns([4,1])
            with col1:
                if st.button(chat_info['title'],key=chat_id,use_container_width=True):
                    select_chat(chat_id)
            with col2:
                if st.button("🗑️",key=f"delete_{chat_id}"):
                    delete_chat(chat_id)

def response_generator(text):
    #text = random.choice(["Hi how can I help you?", "Hi how are you?", "Happy to help you!!"])
    for word in text.split():
        yield word + " "
        time.sleep(0.05)

async def process_message(chat_id,prompt):
    doc = {
        "chat_id":chat_id,
        "content":prompt,
        "username":st.session_state.username
    }
    response = requests.post(f"http://127.0.0.1:8000/process_message",json=doc)
    if response.status_code == 200:
        response_data = response.json()
        return response_data['response']
    else:
        return "Sorry, I encountered an error processing your request"

# if not st.session_state.active_chat_id and st.session_state.chats:
#     if st.session_state.chats:
#         st.session_state.active_chat_id = next(iter(st.session_state.chats))
#     else:
#         st.session_state.active_chat_id = None
#     update_session_cache()

if st.session_state.active_chat_id:
    title = st.session_state.chats[st.session_state.active_chat_id]["title"]
    st.header(f"Chat: {title}")

    if st.session_state.current_chat_history:
        for chat_info in st.session_state.current_chat_history:
            if chat_info["role"] == "human":
                st.chat_message("user").markdown(chat_info["content"])
            elif chat_info["role"] == "ai":
                st.chat_message("assistant").markdown(chat_info["content"])
            

    if prompt := st.chat_input("Type your message..."):
        # insert_response = requests.post(f"http://127.0.0.1:8000/insert_chat_message?chat_id={st.session_state.active_chat_id}&role='human'&content={prompt}")
        # insert_response_data = insert_response.json()
        # print(insert_response_data["messages"])
        st.chat_message("user").markdown(prompt)
        st.session_state.current_chat_history.append({
            "role":"human",
            "content":prompt
        })
        update_session_cache()
        with st.spinner("Thinking..."):
            response_text = asyncio.run(process_message(st.session_state.active_chat_id,prompt))
        ######### work on rag here
        st.chat_message("assistant").write_stream(response_generator(response_text))
        st.session_state.current_chat_history.append({
            "role":"ai",
            "content":response_text
        })
        update_session_cache()
else:
    st.info("Create a new chat to get started!")





