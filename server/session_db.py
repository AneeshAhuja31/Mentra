from fastapi import FastAPI,Cookie,Response
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
from dotenv import load_dotenv
import os
from bson.objectid import ObjectId

load_dotenv()
mongodb_uri = os.getenv('MONGODB_URI')
client = AsyncIOMotorClient(mongodb_uri)

db = client.mentra_db
sessions = db.sessions
users = db.users

async def create_session(user):
    session_id = str(uuid.uuid4())
    await sessions.insert_one({"user_id":str(user["_id"]),"session_id":session_id})
    response =JSONResponse(content = {"result":True,"message":"Login successful!","username":user["username"]})
    response.set_cookie(key="session_id",value=session_id,httponly=True)
    return response

async def validate_session(session_id):
    session = await sessions.find_one({"session_id":session_id})
    if session:
        user = await users.find_one({"_id":ObjectId(session["user_id"])})
        return user
    return False

async def end_session(session_id):
    await sessions.delete_one({"session_id":session_id})
    return True