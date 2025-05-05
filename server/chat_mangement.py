from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import time
load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")
client = AsyncIOMotorClient(mongodb_uri)
db = client.mentra_db
chats = db.chats

async def insert_chat(chat_id,username,title):
    document = {
        "chat_id":chat_id,
        "username":username,
        "title": title
    }
    result = await chats.insert_one(document)

    response = {"message": f"Unable to insert new chat"}
    if result.inserted_id:
        response = {
            "message": f"New chat created with chat_id: {chat_id}"
        }
    return response

async def find_chat(chat_id):
    result = await chats.find_one({"chat_id":chat_id})
    
    response = {
        "chat_found":False,
        "message":f"Chat with chat_id: {chat_id} not found!"
    }
    if result:
        response = {
            "chat_found":True,
            "message":f"Chat with chat_id: {chat_id} found!"
        }
    return response

async def get_chats(username):
    result = await chats.find({"username":username}).to_list(length=None)
    return result

async def delete_chat(chat_id):
    result = await chats.delete_one({"chat_id":chat_id})
    response = {"message":f"Chat with chat_id {chat_id} not found!"}
    if result.deleted_count:
        response = {"message":f"Chat with chat_id: {chat_id} deleted successfully!"}
    return response

    
    
        