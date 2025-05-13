from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")
client = AsyncIOMotorClient(mongodb_uri)
db = client.mentra_db
pdfname = db.pdfname

async def insert_pdf_name(pdf_name,username):
    result = await pdfname.insert_one({"username":username,"pdf_name":pdf_name})
    response  = {"message":"Unable to store pdf name in db"}
    if result.inserted_id:
        response = {"message":f"Stored pdf file: {pdf_name} in db",
                    "file_id":str(result.inserted_id)}
    return response


async def find_pdf_name(username):
    result = await pdfname.find_one({"username":username})
    response = {"bool":False}
    if result:
        response = {
            "bool":True,
            "filename":result["pdf_name"]
        }
    return response



async def delete_pdf_name_and_ats(username):
    result = await pdfname.delete_one({"username":username})
    response = {"deleted":False,"message":f"No PDF name or ats found!"}
    if result.deleted_count:
        response = {"deleted":True,"message":f"Deleted file name and ats of user: {username}"}
    return response


