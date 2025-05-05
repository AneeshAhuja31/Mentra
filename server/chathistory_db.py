from motor.motor_asyncio import AsyncIOMotorClient
from langchain.memory.chat_message_histories import MongoDBChatMessageHistory
from langchain_core.messages import HumanMessage,AIMessage
import os
from dotenv import load_dotenv
load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")
client = AsyncIOMotorClient(mongodb_uri)
chat_histories = client.chat_histories

async def retrieve_chat_history(chat_id):
    history = MongoDBChatMessageHistory(
        session_id=chat_id,
        collection=chat_histories
    )
    return await history.aget_messages()

async def insert_chat_history(chat_id,role:str,content:str):
    history = MongoDBChatMessageHistory(
        session_id=chat_id,
        collection=chat_histories
    )
    if role == "human":
        await history.aadd_messages(HumanMessage(content=content))
    elif role == "ai":
        await history.aadd_messages(AIMessage(content=content))

def get_chat_history():
    return retrieve_chat_history
    
