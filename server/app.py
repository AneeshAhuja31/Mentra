from fastapi import FastAPI,Cookie,Response,Depends
import streamlit as st
from pydantic import BaseModel
from user_database import find_user,insert_user,check_password
from cookie_auth import create_session,validate_session,end_session
from pdfname_db import insert_pdf_name,find_pdf_name,delete_pdf_name
from chatbot import vectorstore_init_faiss,delete_vectorstore_faiss,create_ragchain
from chathistory_adapter import get_chat_history_for_ui,insert_chat_history,delete_chat_history
from chat_mangement import insert_chat,find_chat,get_chats,delete_chat
app = FastAPI()
from fastapi.responses import JSONResponse
import time

class UserRequest(BaseModel):
    username:str
    password:str

class VectorStoreRequest(BaseModel):
    username: str
    splitted_text: list

class ProcessMessageRequest(BaseModel):
    chat_id:str
    content:str
    username:str


@app.post('/login')
async def login(request:UserRequest):
    body = request.dict()
    username = body.get("username")
    password = body.get("password")
    user = await find_user(username)
    if not user:
        response = {"result":False,"message":"Login failed. Username doesn't exist!"}
    else:
        passwordcheck_result = await check_password(username,password)
        if passwordcheck_result:
            response = await create_session(user)
        else:
            response = {"result":False,"message":"Incorrect password!"}
    return response

@app.post('/signup')
async def signup(request:UserRequest):
    body = request.dict()
    username = body.get("username")
    password = body.get("password")
    result = await find_user(username)
    response = ""
    if result:
        response = { 
            "result":False,
            "message":"Error Username already exist!"
        }
    else:
        insert_body = {
            "username":username,
            "password":password
        }
        insert_request = await insert_user(insert_body)
        if insert_request:
            response = {
                "result":True,
                "message":"Signup Successful. You can login in now!"
            } 
            
        else:
            response = {
                "result":False,
                "message":"Signup failed"
            }
    return response

@app.get('/validate_session')
async def validate_user_session(session_id:str = Cookie(None)):
    if not session_id:
        return {"authenticated":False}
    
    user = await validate_session(session_id)
    if user:
        return {"authenticated":True,"username":user["username"]}
    else:
        return {"authenticated":False}

async def get_current_user(session_id:str = Cookie(None)):
    if not session_id:
        return None
    return await validate_session(session_id)


@app.get("/logout")
async def logout(session_id:str = Cookie(None)):
    if session_id:
        await end_session(session_id)
    response = JSONResponse(content={"result":True,"message":"Logged out successfully!"})
    response.delete_cookie(key="session_id")
    return response



@app.post("/initialize_vectorstore")
async def initialize_vectorstore(request:VectorStoreRequest):
    splitted_text = request.splitted_text
    username = request.username
    await vectorstore_init_faiss(text=splitted_text,username=username)
    return {"message": "Vector store initialized successfully"}

@app.delete("/delete_vectorstore")
async def delete_user_vectorstore(username):
    result = await delete_vectorstore_faiss(username)
    return result    

@app.post("/upload_pdf_name")
async def upload_pdf_name_with_username(username,pdf_name):
    return await insert_pdf_name(pdf_name,username)
    

@app.get("/find_pdf_name")
async def find_pdf_name_with_username(username:str):
    return await find_pdf_name(username)
    
    
@app.delete("/delete_pdf_name")
async def delete_pdf_name_with_username(username:str):
    return await delete_pdf_name(username)


@app.post("/new_chat")
async def create_chat(chat_id,username,title):
    return await insert_chat(chat_id,username,title)

@app.get("/find_chat")
async def retrieve_chat(chat_id):
    return await find_chat(chat_id)

@app.get("/get_chat_list")
async def get_chat_list(username):
    return await get_chats(username)

@app.delete("/delete_chat")
async def delete_chat_with_chat_id(chat_id):
    return await delete_chat(chat_id)

@app.get("/get_chat_history_for_ui")
async def get_chat_history_for_ui_by_chat_id(chat_id):
    return await get_chat_history_for_ui(chat_id)

@app.delete("/delete_chat_history")
async def delete_chat_history_by_chat_id(chat_id):
    return await delete_chat_history(chat_id)


@app.post("/process_message")
async def process_manage(request:ProcessMessageRequest):
    chat_id = request.chat_id
    content = request.content
    username = request.username
    await insert_chat_history(chat_id,"human",content)
    
    rag_chain = await create_ragchain(username)
    response = await rag_chain.ainvoke(
        {"input":content},
        config={"configurable":{"session_id":chat_id}}
    )
    await insert_chat_history(chat_id,"ai",response["answer"])
    
    return {"response":response["answer"]}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host='0.0.0.0',port=8000)
    