from motor.motor_asyncio import AsyncIOMotorClient,AsyncIOMotorGridFSBucket
import os
from dotenv import load_dotenv
import uuid
from io import BytesIO
from pypdf import PdfReader
load_dotenv()
mongo_db_uri = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(mongo_db_uri)
db = client.mentra_db
pdffiles = AsyncIOMotorGridFSBucket(db,bucket_name="pdffiles")

async def insert_pdf(file,username):
    file_data = await file.read()
    file_name = file.filename
    file_id = await pdffiles.upload_from_stream(
        file_name,
        file_data,
        metadata={
            "username":username
        }
    )
    return {
        "message":f"Uploaded PDF file: {file_name} with id: {file_id}",
        "file_id": str(file_id)
    }

async def find_pdf(username):
    cursor = pdffiles.find({"metadata.username":username},no_cursor_timeout=True)
    files = await cursor.to_list(length=1)
    if files:
        file = files[0]
        filename = file["filename"]
        result = {
            "bool":True,
            "filename":filename
        }
    else:
        result = {
            "bool":False
        }
    return result

async def delete_pdf(username):
    cursor = pdffiles.find({"metadata.username":username},no_cursor_timeout=True)
    files = await cursor.to_list(length=1)
    if not files:
        return {"deleted":False,"message":f"No PDF found!"}
    file = files[0]
    filename = file["filename"]
    file_id = file["_id"]
    await pdffiles.delete(file_id)
    return {"deleted":True,"message":f"Deleted file: {filename}"}

async def get_pdf(username):
    cursor = pdffiles.find({"metadata.username":username},no_cursor_timeout=True)
    files = await cursor.to_list(length=1)
    if not files:
        return None
    file = files[0]
    file_id = file["_id"]
    grid_out = await pdffiles.open_download_stream(file_id)
    pdf_binary = await grid_out.read()
    # pdf_file = BytesIO(pdf_binary)
    # reader = PdfReader(pdf_file)
    # text = ""
    # for page in reader.pages:
    #     text+=page.extract_text()
    return pdf_binary
    