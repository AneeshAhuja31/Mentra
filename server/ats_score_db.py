from pdfname_db import db
pdfname = db.pdfname

async def insert_ats(username,score,review):
    result = await pdfname.update_one({"username":username,},
                {"$set":{"score":score,"review":review}}
            )
    response = {"message":"Unable to upload ATS"}
    if result.modified_count:
        print("Message Inserted Successfully")
        response = {"message":"Uploaded ATS successfully"}
    return response

async def find_ats(username):
    result = await pdfname.find_one({"username":username})
    response = {"bool":False}
    if result:
        response = {
            "bool":True,
            "ats_score":result["score"],
            "review":result["review"]
        }
    return response    


#the insert ats endpoint is not reaching the backend, there is some error in sending the request
