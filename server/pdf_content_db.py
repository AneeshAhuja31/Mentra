from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")
client = AsyncIOMotorClient(mongodb_uri)
db = client.mentra_db
pdf_content_collection = db.pdf_content

async def insert_pdf_content(pdf_content,username):
    
    result = await pdf_content_collection.insert_one({"username":username,"pdf_content":pdf_content})
    response  = {"message":"Unable to store pdf name in db"}
    if result.inserted_id:
        response = {"message":f"Stored pdf content in db",
                    "file_id":str(result.inserted_id)}
    return response

async def get_pdf_content(username):
    result = await pdf_content_collection.find_one({"username":username})
    return result["pdf_content"]

async def delete_pdf_content(username):
    result = await pdf_content_collection.delete_one({"username":username})
    response = {"deleted":False,"message":f"No PDF name or ats found!"}
    if result.deleted_count:
        response = {"deleted":True,"message":f"Deleted file name and ats of user: {username}"}
    return response
