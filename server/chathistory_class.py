from langchain.schema import BaseChatMessageHistory
from langchain.schema.messages import HumanMessage,AIMessage,BaseMessage
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List,Sequence
import time
import os
from dotenv import load_dotenv
load_dotenv()
mongodb_uri = os.getenv("MONGODB_URI")

class MongoDBChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, connection_string: str, db_name: str, collection_name: str, chat_id: str):
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.chat_id = chat_id
        self.messages:List[BaseMessage] = []
        split_id = self.chat_id.split("_chat_")
        with_chat_ = self.chat_id.removesuffix(split_id[-1])
        self.username = with_chat_.removesuffix("_chat_")
    
    
    
    async def aget_messages(self) -> List:
        if not self.messages:
            cursor = await self.collection.find({"chat_id":self.chat_id}).sort("timestamp",1).to_list(length=None)
            messages = []
            print(f"Found {len(cursor)} messages for chat_id: {self.chat_id}")
            for doc in cursor:
                print(f"Retreived message: {doc}")
                if doc["role"] == "human":
                    messages.append(HumanMessage(content=doc["content"]))
                elif doc["role"] == "ai":
                    messages.append(AIMessage(content=doc["content"]))
                
            self.messages = messages

        return self.messages
    
    async def aadd_messages(self, messages:List[BaseMessage]) -> None:
        msg = messages[0]
        if isinstance(msg,HumanMessage):
            doc = {
                "chat_id":self.chat_id,
                "role":"human",
                "content":msg.content,
                "timestamp":time.time(),
                "username":self.username
            }
        elif isinstance(msg,AIMessage):
            doc = {
                "chat_id":self.chat_id,
                "role":"ai",
                "content":msg.content,
                "timestamp":time.time()
            }
        await self.collection.insert_one(doc)

    async def aclear(self):
        await self.collection.delete_many({"chat_id":self.chat_id})
    
    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        raise NotImplementedError("Use aadd_messages in async code")
    
    def clear(self) -> None:
        raise NotImplementedError("Use aclear in async code")
    
    
def get_chat_history(): #for rag chain
    def get_session_history(session_id:str) -> MongoDBChatMessageHistory:
        return MongoDBChatMessageHistory(
            connection_string=mongodb_uri,
            db_name="mentra_db",
            collection_name="chat_history",
            chat_id=session_id
        )
    return get_session_history
        