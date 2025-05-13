from langchain_groq.chat_models import ChatGroq
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_history_aware_retriever,create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from chathistory_class import get_chat_history
import os
import shutil
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",google_api_key=gemini_api_key)

mongodb_uri = os.getenv("MONGODB_URI")

client = MongoClient(mongodb_uri)
db = client.mentra_db
chat_history_collection = db.chat_history




contextualize_q_prompt = '''
"Given a chat history and the latest user question which might reference context in the chat history,
 formulate a standalone question which can be understood without the chat history. Do NOT answer the 
 question, just reformulate it if needed and otherwise return it as is."
'''

prompt = ChatPromptTemplate.from_messages(
        [
            ("system",contextualize_q_prompt),
            MessagesPlaceholder("chat_history"),
            ("user",'{input}')
        ]
    )



system_prompt = '''
    You are an assistant for question answering tasks and also a mentor providing career and 
    skill guidance based on the resume the user has provided and the tests they have performed. You will use the provided context of the give resume, the test statistics,
    the wrong questions and right questions
    and give answers to the questions based on that. If you dont know the answer say that you don't know. Keep the answer concise 
    by trying to keep it within 4 sentences or less.
    
    User's test performance according to tests given based on skills or project in their resume:
    {test_stats}

    The questions they got wrong on all of the test are as follows:
    {wrong_questions}

    The questions they got right on all of the test are as follows:
    {right_questions}
    
    Resume context:
    {context}
'''
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system",system_prompt),
        MessagesPlaceholder("chat_history"),
        ("user","{input}")
    ]
)
  

async def vectorstore_init_faiss(text,username):
    embeddings = HuggingFaceEmbeddings(model_name = "all-MiniLM-L6-v2")
    user_dir = f"./faiss_index/{username}"
    os.makedirs(user_dir, exist_ok=True)

    vectorstore = FAISS.from_texts(
        texts=text,
        embedding=embeddings
    )
    vectorstore.save_local(user_dir)
    return vectorstore.as_retriever()

async def get_vector_store_retriever_faiss(username):
    embeddings = HuggingFaceEmbeddings(model_name = "all-MiniLM-L6-v2")
    user_dir = f"./faiss_index/{username}"

    vectorstore = FAISS.load_local(user_dir,embeddings,allow_dangerous_deserialization=True)
    return vectorstore.as_retriever()

async def delete_vectorstore_faiss(username):
    user_dir = f"./faiss_index/{username}"
    if not os.path.exists(user_dir):
        return {"success": False, "message": f"No vectorstore found for {username}"}
    try:
        shutil.rmtree(user_dir)
        return {"success":True,"message":f"Vectorstore for {username} deleted successfully"}
    except Exception as e:
        return {"success": False, "message": f"Error deleting vector store: {str(e)}"}

# async def create_conversational_rag_chain(llm,prompt,vectorstore_retriever,qa_prompt):
#     history_aware_chain= create_history_aware_retriever(llm,vectorstore_retriever,prompt)
#     qa_chain = create_stuff_documents_chain(llm,qa_prompt)
#     rag_chain = create_retrieval_chain(history_aware_chain,qa_chain)
#     conversational_rag_chain = RunnableWithMessageHistory(
#         rag_chain,
#         get_chat_history(),
#         input_messages_key="input",
#         history_messages_key="chat_history"
#     )
#     return conversational_rag_chain

# async def create_ragchain(username):
#     vectorstore_retriever = await get_vector_store_retriever_faiss(username)
#     conversational_rag_chain = await create_conversational_rag_chain(llm,prompt,vectorstore_retriever,qa_prompt)
#     return conversational_rag_chain

async def create_conversational_rag_chain(llm, prompt, vectorstore_retriever, qa_prompt, test_stats="No test data available.",wrong_questions_list = [],right_questions_list = []):
    history_aware_chain = create_history_aware_retriever(llm, vectorstore_retriever, prompt)
    
    qa_chain = create_stuff_documents_chain(
        llm, 
        qa_prompt, 
        document_variable_name="context"
    )
    wrong_questions_string = "\n".join(wrong_questions_list)
    right_questions_string = "\n".join(right_questions_list)
    
    retrieval_chain = create_retrieval_chain(history_aware_chain, qa_chain)
    
    combined_chain = RunnablePassthrough.assign(
        test_stats=lambda _: test_stats,
        wrong_questions=lambda _:wrong_questions_string,
        right_questions=lambda _:right_questions_string
    ) | retrieval_chain
    
    conversational_rag_chain = RunnableWithMessageHistory(
        combined_chain,
        get_chat_history(),
        input_messages_key="input",
        history_messages_key="chat_history"
    )
    
    return conversational_rag_chain

async def create_ragchain(username, test_stats="No test data available.",wrong_questions_list=[],right_questions_list=[]):
    vectorstore_retriever = await get_vector_store_retriever_faiss(username)
    custom_qa_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("user", "{input}")
    ])
    
    conversational_rag_chain = await create_conversational_rag_chain(
        llm,
        prompt,
        vectorstore_retriever,
        custom_qa_prompt,
        test_stats=test_stats,
        wrong_questions_list=wrong_questions_list,
        right_questions_list=right_questions_list
    )
    return conversational_rag_chain




