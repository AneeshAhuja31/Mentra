from fastapi import FastAPI
import streamlit as st
from pydantic import BaseModel
from database import find_user,insert_user,check_password

app = FastAPI()

class User_Request(BaseModel):
    username:str
    password:str

@app.post('/login')
async def login(request:User_Request):
    body = request.dict()
    username = body.get("username")
    password = body.get("password")
    namecheck_result = await find_user(username)
    if not namecheck_result:
        response = {"result":False,"message":"Login failed. Username doesn't exist!"}
    else:

        passwordcheck_result = await check_password(username,password)
        if passwordcheck_result:
            response = {"result":True,"message":"Login successful!"}
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
                "message":"Signup Successful"
            } 
            
        else:
            response = {
                "result":False,
                "message":"Signup failed"
            }
    return response
        
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host='0.0.0.0',port=8000)
    