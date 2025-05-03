from langchain_groq.chat_models import ChatGroq
from langchain_core.messages import HumanMessage,SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import CharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(api_key=groq_api_key,model="Llama3-8b-8192")

system = '''
    You are an assistant for question answering tasks. 
    Use the following pieces of retrieved context to answer the question.
    If you don't know the answer, say that you don't know.
    Use three sentences maximum and keep the answers concise. \n\n
    {context}
'''
def split_text(raw_text):
    text_splitter = CharacterTextSplitter(chunk_size = 500,chunk_overlap=50)
    return text_splitter.split_text(raw_text)

def vectorstore_init(text):
    embeddings = HuggingFaceEmbeddings(model_name = "all-MiniLM-L6-v2")
    vectorstore = Chroma.from_texts(texts=text,embedding=embeddings)
    return vectorstore

prompt = ChatPromptTemplate.from_messages(
    [
        ("system")
    ]
)

