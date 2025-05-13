from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
import time
from bson import ObjectId
load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")
client = AsyncIOMotorClient(mongodb_uri)
db = client.mentra_db
chats = db.chats

async def insert_chat(chat_id,username,title):
    document = {
        "chat_id":chat_id,
        "username":username,
        "title": title,
        "bookmarked":False,
        "updated_at":time.strftime("%Y-%m-%d %H:%M:%S")
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
def serialize_document(document):
    if isinstance(document, dict):
        return {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in document.items()}
    return document

async def get_chats(username):
    result = await chats.find({"username":username}).to_list(length=None)
    chat_list = [serialize_document(chat) for chat in result]
    return {"chat_list":chat_list}


async def delete_chat(chat_id):
    result = await chats.delete_one({"chat_id":chat_id})
    response = {"message":f"Chat with chat_id {chat_id} not found!"}
    if result.deleted_count:
        response = {"message":f"Chat with chat_id: {chat_id} deleted successfully!"}
    return response

async def delete_chat_list(username:str):
    result = await chats.delete_many({"username":username})
    response = {"message":f"No chats found for {username}"}
    if result.deleted_count:
        response = {"message":f"Deleted all chats of {username}"}
    return response

async def bookmark_chat(chat_id):
    result = await chats.update_one(
        {"chat_id":chat_id},
        {"$set":{"bookmarked":True,"updated_at":time.strftime("%Y-%m-%d %H:%M:%S")}}
    )
    response = {"updated":False,"message":"Error in bookmarking chat"}
    if result.modified_count:
        response = {"updated":True,
                    "message":"Successfully bookmarked chat!"}
    return response

async def find_bookmarks(username):
    result = await chats.find({"username":username,"bookmarked":True}).sort("bookmarked_at",-1).to_list(length=None)
    response = {"bool":False,"message":"No Chats bookmarked!","bookmarked_chats_list":[]}
    if len(result):
        response = {"bool":True,"bookmarked_chats_list":[serialize_document(chat) for chat in result]}
    return response

async def get_chats(username):
    result = await chats.find({"username":username}).to_list(length=None)
    chat_list = [serialize_document(chat) for chat in result]
    return {"chat_list":chat_list}

async def unbookmark_chat(chat_id):
    result = await chats.update_one({"chat_id":chat_id},
                                    {"$set":{"bookmarked":False,"updated_at":time.strftime("%Y-%m-%d %H:%M:%S")}})
    response = {"updated":False,"message":"Error in unbookmarking chat"}
    if result.modified_count:
        response =  {"updated":True,"message":"Successfully unbookmarked chat!"}
    return response
    
    



    
    
        