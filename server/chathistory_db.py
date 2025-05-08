from motor.motor_asyncio import AsyncIOMotorClient
from langchain_core.messages import HumanMessage,AIMessage
import os
import time
from dotenv import load_dotenv
import chathistory_db
load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")
client = AsyncIOMotorClient(mongodb_uri)
db = client.mentra_db
chat_histories = db.chat_history

async def retrieve_chat_history(chat_id,rag=True):
    chat_history_list = await chat_histories.find({"chat_id":chat_id}).sort("timestamp",1).to_list(length=None)
    if rag: #to input as chat history in rag chain
        messages = []
        for chat_history in chat_history_list:
            chat_content = chat_history["content"]
            if chat_history["role"] == "human":
                messages.append(HumanMessage(content=chat_content))
            elif chat_history["role"] == "ai":
                messages.append(AIMessage(content=chat_content))
        return messages
    else:
        return chat_history_list #to display on frontend ui

async def insert_chat_message(chat_id:str,role:str,content:str):
    document = {
        "chat_id":chat_id,
        "role":role,
        "content":content,
        "timestamp":time.time()
    }
    result = await chat_histories.insert_one(document)
    response = {"message":f"ERROR in inserting {role} message of {chat_id}"}
    if result.inserted_id:
        response = {"message":f"{role} message of {chat_id} inserted successfully!"}
    return response
    
    

async def delete_chat_history(chat_id):
    result = await chat_histories.delete_many({"chat_id":chat_id})
    response = {"message":f"ERROR in deleting chat history of {chat_id}"}
    if result.deleted_count:
        response = {"message":f"Deleted chat history of {chat_id}"}
    
    return response

    
def get_chat_history():
    return retrieve_chat_history
    
