from motor.motor_asyncio import AsyncIOMotorClient
import os
import time
from dotenv import load_dotenv
load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")
client = AsyncIOMotorClient(mongodb_uri)
db = client.mentra_db
test_score = db.test_score

async def insert_test_score(username:str,score:int):
    result = await test_score.insert_one({"username":username,"score":score,"timestamp":time.time()})
    response = {"message":f"Unable to insert test score for {username}"}
    if result.inserted_id:
        response = {"message":f"Inserted test score for {username}"}
    return response

async def get_test_score_list(username:str):
    test_score_list = await test_score.find({"username":username}).sort("timestamp",1).to_list(length=None)

    if len(test_score_list) == 0: 
        return {"test_score_list":[],"average":0}

    test_score_list_response = []
    sum = 0
    for score_doc in test_score_list:
        sum += int(score_doc['score'])
        test_score_list_response.append(
            {
                "score":score_doc["score"]
            }
        )
    avg = sum/len(test_score_list)
    return {"test_score_list":test_score_list_response,"average":avg}


