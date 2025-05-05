from fastapi import FastAPI,Cookie,Response,Depends
import streamlit as st
from pydantic import BaseModel
from user_database import find_user,insert_user,check_password
from cookie_auth import create_session,validate_session,end_session
from pdf_gridfs_db import insert_pdf,find_pdf,delete_pdf,get_pdf
from chatbot import create_conversational_rag_chain
from chathistory_db import get_chat_history,retrieve_chat_history
from chat_mangement import insert_chat,find_chat,get_chats,delete_chat
from fastapi import UploadFile,Form
app = FastAPI()
from fastapi.responses import JSONResponse

class User_Request(BaseModel):
    username:str
    password:str

class Upload_Request(BaseModel):
    file:UploadFile

@app.post('/login')
async def login(request:User_Request):
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
async def signup(request:User_Request):
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

@app.post("/upload_pdf")
async def upload_pdf(file:UploadFile,username:str = Form(...)):
    pdf_upload_data = await insert_pdf(file,username)
    
    response = {}
    if pdf_upload_data:
        message = pdf_upload_data['message']
        file_id = str(pdf_upload_data['file_id'])
        response = JSONResponse(content={
            "message":message,
            "file_id":file_id
        })
    else:
        response = JSONResponse(content={
            "message": "Failed to upload pdf to db"
        })
    return response
    # if file:
    #     reader = PdfReader(file)
    #     raw_data = ""
    #     for page in reader.pages:
    #         raw_data+=page.extract_text()

@app.get("/find_pdf")
async def find_pdf_with_username(username:str):
    return await find_pdf(username)
    
    
@app.delete("/delete_pdf")
async def delete_pdf_with_username(username:str):
    return await delete_pdf(username)


# @app.post("/create_ragchain")
# async def create_ragchain(username):
#     pdf_content = await get_pdf(username)
#     splitted_text = await split_text(pdf_content)
#     vectorstore_retriever = await vectorstore_init(splitted_text,username)
#     conversational_rag_chain = await create_conversational_rag_chain(llm,prompt,vectorstore_retriever,qa_prompt)

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

@app.get("/get_history")
async def get_history(chat_id):
    return await retrieve_chat_history(chat_id)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host='0.0.0.0',port=8000)
    