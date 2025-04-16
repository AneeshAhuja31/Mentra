from fastapi import FastAPI,Cookie,Response
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
from dotenv import load_dotenv
import os
load_dotenv()
mongodb_uri = os.getenv('MONGODB_URI')
client = AsyncIOMotorClient(mongodb_uri)

db = client.mentra_db
sessions = db.sessions
users = db.users

async def create_session(user):
    session_id = str(uuid.uuid4())
    sessions.insert_one({"user_id":str(user["_id"]),"session_id":session_id})
    response =JSONResponse(content = {"result":True,"message":"Login successful!","username":user["username"]})
    response.set_cookie(key="session_id",value=session_id,httponly=True)
    return response
    
