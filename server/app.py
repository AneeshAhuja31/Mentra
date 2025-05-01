from fastapi import FastAPI,Cookie,Response,Depends
import streamlit as st
from pydantic import BaseModel
from database import find_user,insert_user,check_password
from cookie_auth import create_session,validate_session,end_session
app = FastAPI()
from fastapi.responses import JSONResponse
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host='0.0.0.0',port=8000)
    