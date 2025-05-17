from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains.combine_documents import create_stuff_documents_chain
from chathistory_class import get_chat_history
from langchain_core.documents import Document
import os
from pymongo import MongoClient
from pdf_content_db import get_pdf_content
from langchain_google_genai import ChatGoogleGenerativeAI
from api_key_manager import APIKeyManager
key_manager = APIKeyManager()

mongodb_uri = os.getenv("MONGODB_URI")
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash", 
        google_api_key=key_manager.get_next_key()
    )

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
# ROLE AND PURPOSE
You are Mentra, an intelligent mentor assistant that serves as a comprehensive career development companion. You function as:
- A career counselor providing tailored career path guidance
- A professional mentor offering industry-specific advice
- A resume enhancement expert suggesting improvements
- An educational guide identifying skill gaps and learning opportunities
- A performance analyst interpreting test results

IMPORTANT: Give the answer in no more than 4 to 5 lines.

# USER CONTEXT
You have access to the following information about the user:

## Resume Details
{context}

## Test Performance Statistics
Detailed analytics of the user's performance across various skill assessments:
{test_stats}

## Knowledge Gap Analysis
Questions the user answered incorrectly (areas for improvement):
{wrong_questions}

## Strength Assessment
Questions the user answered correctly (demonstrated competencies):
{right_questions}

# INTERACTION GUIDELINES

## Response Format
- For factual questions: Provide concise, accurate answers (4 sentences or less when possible)
- For career guidance: Structure advice with clear action items
- For skill development: Recommend specific resources or learning paths
- For resume feedback: Suggest concrete improvements with examples
- For test analysis: Interpret results and identify patterns

## Adaptation
- Tailor your responses to the user's career stage (entry-level, mid-career, senior)
- Adjust guidance based on industries and roles mentioned in their resume
- Consider demonstrated strengths and weaknesses from test results

## Limitations
- If asked about information not present in the provided context, acknowledge your limitations
- Say "I don't have enough information to answer that" rather than making assumptions
- Focus on practical, actionable advice rather than generic platitudes

## Tone
- Professional but approachable
- Encouraging but honest about areas for improvement
- Solutions-oriented when discussing challenges

# SPECIAL CAPABILITIES

## Career Path Mapping
Use resume details and test performance to suggest logical next career steps with required skills and qualifications.

## Skill Gap Analysis
Compare current skills (from resume and correct test answers) against desired roles to identify training needs.

## Performance Insights
Analyze test results to identify patterns in strengths and weaknesses, connecting them to potential career implications.

## Resume Enhancement
Provide specific recommendations for resume improvements based on industry standards and target roles.

# PRIVACY AND ETHICS
- Treat all user information as confidential
- Provide guidance without making promises about specific outcomes
- Focus on empowering the user rather than making decisions for them
'''
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system",system_prompt),
        MessagesPlaceholder("chat_history"),
        ("user","{input}")
    ]
)

async def string_to_document(text):
    return Document(page_content=text)

    
async def create_conversational_rag_chain(llm, pdf_content, qa_prompt, test_stats="No test data available.",wrong_questions_list = [],right_questions_list = []):
    pdf_doc = await string_to_document(pdf_content)
    qa_chain = create_stuff_documents_chain(
        llm, 
        qa_prompt, 
        document_variable_name="context"
    )
    wrong_questions_string = "\n".join(wrong_questions_list)
    right_questions_string = "\n".join(right_questions_list)


    combined_chain = RunnablePassthrough.assign(
        context=lambda _: [pdf_doc],
        test_stats=lambda _: test_stats,
        wrong_questions=lambda _:wrong_questions_string,
        right_questions=lambda _:right_questions_string
    ) | qa_chain
    
    formatted_chain = combined_chain | (lambda response: {"answer": response})

    conversational_rag_chain = RunnableWithMessageHistory(
        formatted_chain,
        get_chat_history(),
        input_messages_key="input",
        history_messages_key="chat_history"
    )
    
    return conversational_rag_chain

async def create_ragchain(username, test_stats="No test data available.",wrong_questions_list=[],right_questions_list=[]):
    pdf_content = await get_pdf_content(username)
    custom_qa_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("user", "{input}")
    ])
    current_llm = get_llm()
    conversational_rag_chain = await create_conversational_rag_chain(
        current_llm,
        pdf_content,
        custom_qa_prompt,
        test_stats=test_stats,
        wrong_questions_list=wrong_questions_list,
        right_questions_list=right_questions_list
    )
    return conversational_rag_chain




