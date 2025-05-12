from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",google_api_key=gemini_api_key)

base_prompt = """Based on the resume information, create EXACTLY 10 multiple-choice questions.

IMPORTANT: Format each question strictly like this with no deviations:
[Single line question text]
[Option 1]
[Option 2]
[Option 3]
[Option 4]
[Exact text of the correct option]

Separate each question with exactly one blank line.
There should be only one new line between the question and it's respective options.
There should be only one new line between each of the choices
There should be only one new line between option 4 and the eact text of the correct option.
Do NOT repeat the question text.
Do NOT include any question numbers, prefixes, or labels.
Do NOT include "Correct option text:" or any similar prefix in the answer line.
Do NOT include option letters (A, B, C, D) before any options.

Make challenging technical questions about the specific skills in the resume.
Find skills mentioned in there resume which may or may not be in their projects 
and ask technical questions based on their context not neccessarily the project itself. 
DO NOT question anything personal or about personal experiences.

Do NOT add any text in the response other than the format specified.

The resume:
{context}
"""

qna_prompt = ChatPromptTemplate.from_template(base_prompt)

async def split_response(response):
    paras = response.split("\n\n")
    qna_list = []
    try:
        for i,para in enumerate(paras):
            lines = para.split('\n')
            question = lines[0]
            choices = [lines[1],lines[2],lines[3],lines[4]]
            correct_option = lines[5]
            qna_list.append({"q_no":i+1,"question":question,"choices":choices,"answer":correct_option})
    except Exception as e:
        print(e)
        return []
    
    return qna_list

async def return_context_from_faiss_vectorstore(username):
    embeddings = HuggingFaceEmbeddings(model_name = "all-MiniLM-L6-v2")
    user_dir = f"./faiss_index/{username}"

    vectorstore = FAISS.load_local(user_dir,embeddings,allow_dangerous_deserialization=True)
    all_docs = list(vectorstore.docstore._dict.values())
    context = "\n\n".join([doc.page_content for doc in all_docs])
    return context

async def generate_qna(username):
    context = await return_context_from_faiss_vectorstore(username)
    chain = qna_prompt|llm|StrOutputParser()
    response = await chain.ainvoke({"context":context})
    qna_list = await split_response(response)
    return {"qna_list":qna_list}
