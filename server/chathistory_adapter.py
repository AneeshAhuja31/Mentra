from motor.motor_asyncio import AsyncIOMotorClient
import os
import time
from dotenv import load_dotenv
from langchain.schema.messages import HumanMessage,AIMessage
load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")
client = AsyncIOMotorClient(mongodb_uri)
db = client.mentra_db
chat_history = db.chat_history

async def insert_chat_history(chat_id:str,role:str,content:str,username:str):
    result = await chat_history.insert_one({
        "chat_id":chat_id,
        "role":role,
        "content":content,
        "username":username,
        "timestamp":time.time()
    })
    response = {"message":f"Unable to insert chat history for {chat_id}"}
    if result.inserted_id:
        response = {"message":f"Inserted chat history for {chat_id}"}
    return response

async def get_chat_history_for_ui(chat_id:str):
    chat_history_list = await chat_history.find({"chat_id":chat_id}).sort("timestamp",1).to_list(length=None)
    messages = []
    for msg in chat_history_list:
        messages.append({
            "role":msg["role"],
            "content":msg["content"]
        })
    return messages

async def delete_chat_history(chat_id:str):
    delete_response = await chat_history.delete_many({"chat_id":chat_id})
    response = {
        "deleted":False,
        "message":f"Unable to deleted / Chat history of {chat_id} not found!"
    }
    if delete_response.deleted_count:
        response = {
            "deleted":True,
            "message":f"Deleted chat history of {chat_id}"
        }
    return response

async def delete_complete_chat_history(username):
    delete_response = await chat_history.delete_many({"username":username})
    response = {
        "deleted":False,
        "message":f"Unable to deleted / Chat history of {username} not found!"
    }
    if delete_response.deleted_count:
        response = {
            "deleted":True,
            "message":f"Deleted complete chat history of {username}"
        }
    return response
    
