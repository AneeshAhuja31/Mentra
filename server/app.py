from fastapi import FastAPI,Cookie,Response
import streamlit as st
from pydantic import BaseModel
from database import find_user,insert_user,check_password
from cookie_auth import create_session
app = FastAPI()

class User_Request(BaseModel):
    username:str
    password:str

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
            response = create_session(user)
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

# @app.get('/validate_session')
# async def validate_user_session(session_id:str = Cookie(None)):
        
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host='0.0.0.0',port=8000)
    