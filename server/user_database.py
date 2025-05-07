from motor.motor_asyncio import AsyncIOMotorClient,AsyncIOMotorGridFSBucket
from passlib.context import CryptContext
import os
import uuid
from dotenv import load_dotenv
load_dotenv()
mongodb_uri = os.getenv("MONGODB_URI") 
client = AsyncIOMotorClient(mongodb_uri)
db = client.mentra_db
users = db.users

pwd_context = CryptContext(schemes=['bcrypt'],deprecated='auto')

async def insert_user(document):
    password = document['password']
    hashed_pwd = pwd_context.hash(password)
    document['password']=hashed_pwd
    result = await users.insert_one(document)
    if result.inserted_id:
        print(f"User Credential Inserted: {result.inserted_id}")
        return True
    else:
        return False

async def find_user(username):
    result = await users.find_one({"username":username})
    return result

async def check_password(username,password):
    user = await find_user(username)
    if user:
        stored_password = user['password']
        return pwd_context.verify(password,stored_password)
    return False


    
    

