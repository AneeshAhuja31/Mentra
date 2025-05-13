from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")
client = AsyncIOMotorClient(mongodb_uri)
db = client.mentra_db
questions = db.questions

async def initialize_questions(username):
    insert_result = await questions.insert_one({"username":username,"wrong_questions":[],"right_questions":[]})
    response = {"bool":False,"message":f"Error in initializing questions"}
    if insert_result.inserted_id:
        response = {"bool":True,"message":f"Successfully initialized messages for {username}"}
    return response

async def update_questions(username,wrong_questions,right_questions):
    existing_result = await questions.find_one({"username":username})
    existing_wrong_questions = existing_result["wrong_questions"]
    existing_right_questions = existing_result["right_questions"]

    update_result = await questions.update_one(
        {"username":username},
        {"$set":
            {
                "wrong_questions":existing_wrong_questions+wrong_questions,
                "right_questions":existing_right_questions+right_questions
            }
        }
    )
    response = {"bool":False,"message":f"Unable to update questions for {username}"}
    if update_result.modified_count:
        response = {"bool":True,"message":f"Successfully update questions for {username}"}
    return response

async def retrieve_questions(username):
    result = await questions.find_one({"username":username})
    wrong_questions = result["wrong_questions"]
    right_questions = result["right_questions"]
    return wrong_questions,right_questions

async def delete_questions(username):
    delete_result = await questions.delete_one({"username":username})
    response = {"bool":False,"message":f"Unable to delete questions for {username}"}
    if delete_result.deleted_count:
        response = {"bool":True,"message":f"SUccessfully deleted questions for {username}"}
    return response