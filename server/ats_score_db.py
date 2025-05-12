from pdfname_db import db
ats_score_collection = db.ats_score

async def insert_ats(username,score,review):
    result = await ats_score_collection.insert_one({
        "username":username,
        "score":score,
        "review":review
    })
    response = {"message":"Unable to upload ATS"}
    if result.inserted_id:
        response = {"message":"Uploaded ATS successfully"}
    return response

async def find_ats(username):
    result = await ats_score_collection.find_one({"username":username})
    response = {"bool":False}
    if result:
        response = {
            "bool":True,
            "ats_score":result["score"],
            "review":result["review"]
        }
    return response    

async def delete_ats(username):
    result = await ats_score_collection.delete_one({"username":username})
    response = {"deleted":False,"message":f"No ATS found"}
    if result.deleted_count:
        response = {"deleted":True,"message":f"Deleted ATS of user: {username}"}
    return response

