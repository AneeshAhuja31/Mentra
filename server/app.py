from fastapi import FastAPI,Cookie
from pydantic import BaseModel
from pdfname_db import insert_pdf_name,find_pdf_name,delete_pdf_name_and_ats
from chatbot import vectorstore_init_faiss,delete_vectorstore_faiss,create_ragchain
from chathistory_adapter import get_chat_history_for_ui,insert_chat_history,delete_chat_history,delete_complete_chat_history
from chat_mangement import insert_chat,find_chat,get_chats,delete_chat,delete_chat_list,bookmark_chat,find_bookmarks,unbookmark_chat
from qna_generator import generate_qna
from test_score_db import insert_test_score, get_test_score_list, delete_test_scores  
from user_database import find_user,insert_user,check_password
from session_db import create_session,validate_session,end_session
from ats_generator import generate_ats_response
from ats_score_db import insert_ats,find_ats
from questions_results import initialize_questions,update_questions,delete_questions,retrieve_questions
from cl_generator import generate_cover_letter
from fastapi.responses import JSONResponse
from typing import List
app = FastAPI()

class UserRequest(BaseModel):
    username:str
    password:str

class VectorStoreRequest(BaseModel):
    username: str
    splitted_text: list

class ProcessMessageRequest(BaseModel):
    chat_id:str
    content:str
    username:str

class InsertATSRequest(BaseModel):
    username:str
    ats_score:int
    ats_review:str

class UpdateQuestionsRequest(BaseModel):
    username:str
    wrong_questions:List[str]
    right_questions:List[str]

class CoverLetterRequest(BaseModel):
    username:str
    job_description:str
    hiring_manager:str
    company_name:str


@app.post('/login')
async def login(request:UserRequest):
    body = request.dict()
    username = body.get("username")
    password = body.get("password")
    user = await find_user(username)
    if not user:
        response = {"result":False,"message":"Login failed. Username doesn't exist!"}
    else:
        passwordcheck_result = await check_password(username,password)
        if passwordcheck_result:
            response = await create_session(user)
        else:
            response = {"result":False,"message":"Incorrect password!"}
    return response

@app.post('/signup')
async def signup(request:UserRequest):
    body = request.dict()
    username = body.get("username")
    password = body.get("password")
    result = await find_user(username)
    response = ""
    if result:
        response = { 
            "result":False,
            "message":"Error Username already exist!"
        }
    else:
        insert_body = {
            "username":username,
            "password":password
        }
        insert_request = await insert_user(insert_body)
        if insert_request:
            response = {
                "result":True,
                "message":"Signup Successful. You can login in now!"
            } 
            
        else:
            response = {
                "result":False,
                "message":"Signup failed"
            }
    return response

@app.get('/validate_session')
async def validate_user_session(session_id:str = Cookie(None)):
    if not session_id:
        return {"authenticated":False}
    
    user = await validate_session(session_id)
    if user:
        return {"authenticated":True,"username":user["username"]}
    else:
        return {"authenticated":False}

async def get_current_user(session_id:str = Cookie(None)):
    if not session_id:
        return None
    return await validate_session(session_id)


@app.get("/logout")
async def logout(session_id:str = Cookie(None)):
    if session_id:
        await end_session(session_id)
    response = JSONResponse(content={"result":True,"message":"Logged out successfully!"})
    response.delete_cookie(key="session_id")
    return response


@app.post("/initialize_vectorstore")
async def initialize_vectorstore(request:VectorStoreRequest):
    splitted_text = request.splitted_text
    username = request.username
    await vectorstore_init_faiss(text=splitted_text,username=username)
    return {"message": "Vector store initialized successfully"}

@app.delete("/delete_vectorstore")
async def delete_user_vectorstore(username):
    result = await delete_vectorstore_faiss(username)
    return result    

@app.post("/upload_pdf_name")
async def upload_pdf_name_with_username(username,pdf_name):
    return await insert_pdf_name(pdf_name,username)
    

@app.get("/find_pdf_name")
async def find_pdf_name_with_username(username:str):
    return await find_pdf_name(username)
    
    
@app.delete("/delete_pdf_name_and_ats")
async def delete_pdf_name_with_username(username:str):
    return await delete_pdf_name_and_ats(username)


@app.post("/new_chat")
async def create_chat(chat_id,username,title):
    return await insert_chat(chat_id,username,title)

@app.get("/find_chat")
async def retrieve_chat(chat_id):
    return await find_chat(chat_id)



@app.get("/get_chat_list")
async def get_chat_list(username):
    return await get_chats(username)

@app.delete("/delete_chat")
async def delete_chat_with_chat_id(chat_id):
    return await delete_chat(chat_id)

@app.delete("/delete_chat_list")
async def delete_chat_list_with_username(username:str):
    return await delete_chat_list(username)


@app.get("/get_chat_history_for_ui")
async def get_chat_history_for_ui_by_chat_id(chat_id):
    return await get_chat_history_for_ui(chat_id)

@app.delete("/delete_chat_history_by_chat_id")
async def delete_chat_history_by_chat_id(chat_id):
    return await delete_chat_history(chat_id)

@app.delete("/delete_complete_chat_history")
async def delete_chat_history_by_username(username):
    return await delete_complete_chat_history(username)


@app.post("/process_message")
async def process_manage(request: ProcessMessageRequest):
    chat_id = request.chat_id
    content = request.content
    username = request.username
    await insert_chat_history(chat_id, "human", content, username)
    
    test_scores_data = await get_test_score_list(username)
    
    scores = [int(item['score']) for item in test_scores_data["test_score_list"]]
    
    test_stats = "No test data available."
    if scores:
        avg_score = sum(scores) / len(scores)
        max_score = max(scores) if scores else 0
        test_stats = f"""Average test score: {avg_score:.2f}/10, Best score: {max_score}/10, Total tests taken: {len(scores)}
        Score of tests in order: {scores}
        """

    wrong_questions_list,right_questions_list = await retrieve_questions(username)

    rag_chain = await create_ragchain(username, test_stats,wrong_questions_list,right_questions_list)
    
    response = await rag_chain.ainvoke(
        {"input": content},
        config={"configurable": {"session_id": chat_id}}
    )
    
    await insert_chat_history(chat_id, "ai", response["answer"], username)
    return {"response": response["answer"]}

@app.get("/generate_qna")
async def generate_qna_with_username(username):
    return await generate_qna(username)

@app.post("/insert_test_score")
async def insert_test_score_by_username(username,score):
    return await insert_test_score(username,score)

@app.get("/get_test_score_list")
async def get_test_score_list_by_username(username):
    return await get_test_score_list(username)

@app.delete("/delete_test_scores")
async def delete_test_scores_endpoint(username: str):
    return await delete_test_scores(username)

@app.get("/generate_ats")
async def generate_ats_by_username(username):
    return await generate_ats_response(username)

@app.post("/insert_ats")
async def insert_ats_by_username(request:InsertATSRequest):
    username = request.username
    score = request.ats_score
    review = request.ats_review
    return await insert_ats(username,score,review)

@app.get("/find_ats")
async def find_ats_by_username(username):
    return await find_ats(username)


@app.post("/bookmark_chat")
async def bookmark_chat_by_chat_id(chat_id):
    return await bookmark_chat(chat_id)

@app.get("/find_bookmarks")
async def get_bookmarks(username):
    return await find_bookmarks(username)

@app.post("/unbookmark_chat")
async def unbookmark_chat_by_chat_id(chat_id):
    return await unbookmark_chat(chat_id)

@app.post("/init_questions")
async def init_questions_on_pdf_upload(username):
    return await initialize_questions(username)

@app.put("/update_questions")
async def update_questions_after_test(request:UpdateQuestionsRequest):
    username = request.username
    wrong_questions = request.wrong_questions
    right_questions = request.right_questions
    return await update_questions(username,wrong_questions,right_questions)

@app.delete("/delete_questions")
async def delete_questions_on_removing_pdf(username):
    return await delete_questions(username)

@app.post("/generate_cl")
async def generate_cl(request:CoverLetterRequest):
    username = request.username
    job_description = request.job_description
    hiring_manager = request.hiring_manager
    if hiring_manager == "":
        hiring_manager == "Hiring Manager"
    company_name = request.company_name
    text = await generate_cover_letter(username,job_description,hiring_manager,company_name)
    return {"text":text}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
    