from langchain_groq.chat_models import ChatGroq
from langchain_core.messages import HumanMessage,SystemMessage
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_history_aware_retriever,create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from chathistory_class import get_chat_history
import os
import shutil
from io import BytesIO
from dotenv import load_dotenv
from pypdf import PdfReader
from pymongo import MongoClient
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(api_key=groq_api_key,model="Llama3-8b-8192")

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
    skill guidance based on the resume the user has provided. You will use the provided context of the give resume
    and give answers to the questions based on that. If you dont know the answer say that you don't know. Keep the answer concise 
    by trying to keep it within 4 sentences or less \n\n
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

async def create_conversational_rag_chain(llm,prompt,vectorstore_retriever,qa_prompt):
    history_aware_chain= create_history_aware_retriever(llm,vectorstore_retriever,prompt)
    qa_chain = create_stuff_documents_chain(llm,qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_chain,qa_chain)
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_chat_history(),
        input_messages_key="input",
        history_messages_key="chat_history"
    )
    return conversational_rag_chain

async def create_ragchain(username):
    vectorstore_retriever = await get_vector_store_retriever_faiss(username)
    conversational_rag_chain = await create_conversational_rag_chain(llm,prompt,vectorstore_retriever,qa_prompt)
    return conversational_rag_chain


