from qna_generator import llm
from pdf_content_db import get_pdf_content
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
base_prompt = '''You are an expert ATS (Applicant Tracking System) analyzer and resume reviewer. Your task is to analyze the provided resume and rate it out of 100 based strictly on the factors provided below.

Format your response exactly as follows:

[numerical score]/100
[Your in detail 1 paragraph review here]

IMPORTANT: Follow the exact format above and do NOT return anything else.
DO NOT add words such as SCORE: or anything of the sort before the numerical score.
DO NOT add words such as REVIEW: or ANALYSIS: or anything else of the sort before the review.

SCORING CRITERIA (strict evaluation required):
- 90-100: Outstanding. Resume is nearly flawless and tailored to current hiring standards.
- 80-89: Strong. Minor improvements possible but already well-optimized.
- 70-79: Good but needs several improvements to stand out.
- 60-69: Average. Requires meaningful updates across several sections.
- Below 60: Weak. Lacks key information, clarity, or formatting expected by modern ATS systems.

1. Provide a score out of 100 based on the following factors:
   - Relevance to the job market (20 points)
   - Content quality and impact statements (20 points)
   - Skills and qualifications (20 points)
   - Formatting and organization (15 points, detailed breakdown below)
   - Grammar and clarity (15 points)
   - Overall impression (10 points)

STRUCTURE AND FORMAT EVALUATION CRITERIA (for the 15 formatting points):
   - Clear section headers (Education, Experience, Skills, etc.) (3 points)
   - Consistent formatting of dates, job titles, and organizations (3 points)
   - Proper use of bullet points for achievements (3 points)
   - Appropriate white space and margins (2 points)
   - Professional fonts and sizing (2 points)
   - Logical ordering of information (most relevant/recent first) (2 points)

2. Give a concise 3-5 line review that:
   - Highlights the resume's greatest strengths
   - Points out 1-2 key areas for improvement, especially regarding structure if applicable
   - Offers practical advice to improve the resume's effectiveness and ATS compatibility

DO NOT inflate scores. Only resumes that excel in nearly every category should receive 85 or above.
When evaluating structure, be extremely critical of inconsistencies, cramped layouts, and poor visual hierarchy.

**IMPORTANT** YOU MUST BE STRICT.

If the uploaded file is not a resume or is not in text format, return the following:

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
    context = await get_pdf_content(username)
    chain = qna_prompt|llm|StrOutputParser()
    text = await chain.ainvoke({"resume_text":context})
    score,review = await split_response(text)
    print(score)
    print(review)
    return {
        "ats_score":score,
        "ats_review":review
    }

