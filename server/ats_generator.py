from qna_generator import llm,return_context_from_faiss_vectorstore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
base_prompt = '''You are an expert ATS (Applicant Tracking System) analyzer and resume reviewer. Your task is to analyze the provided resume and rate it out of 100 based on the factor provided.

Format your response exactly as follows:

[numerical score]/100
[Your 3-5 line review here]

IMPORTANT: Follow the exact format above and do NOT return anything else.
DO NOT add words such as SCORE: or anything of the sort before the numerical score.
DO NOT add words such as REVIEW: or ANALYSIS: or anything else or the sort before the review.

1. Provide a score out of 100 based on the following criteria:
   - Relevance to the job market (20 points)
   - Content quality and impact statements (20 points)
   - Skills and qualifications (20 points)
   - Formatting and organization (15 points)
   - Grammar and clarity (15 points)
   - Overall impression (10 points)

2. Give a concise 3-5 line review that:
   - Highlights the resume's greatest strengths
   - Points out 1-2 key areas for improvement
   - Provides actionable advice to improve the overall quality

If you feel like the uploaded file is not a resume give the exact following response:

0/100
The file you have uploaded is not a resume or it may not be in text format.

Resume to analyze:

{resume_text}
'''
qna_prompt = ChatPromptTemplate.from_template(base_prompt)

async def split_response(text):
    lines = text.split('\n')
    numerator = lines[0].split('/')[0]
    score = int(numerator)
    review = "\n".join(lines[1:])
    return score, review


async def generate_ats_response(username):
    context = await return_context_from_faiss_vectorstore(username)
    chain = qna_prompt|llm|StrOutputParser()
    text = await chain.ainvoke({"resume_text":context})
    score,review = await split_response(text)
    print(score)
    print(review)
    return {
        "ats_score":score,
        "ats_review":review
    }

