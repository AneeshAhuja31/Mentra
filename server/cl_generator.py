from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from qna_generator import return_context_from_faiss_vectorstore,llm

base_prompt = """
Generate a professional cover letter using the format below. Fill in all placeholders based on the provided applicant and job details.

---
[Applicant's Full Name (must be in resume, if not given in resume say that it it not specified in resume.)]
[Email Address (include only if provided in resume)] 
[Phone Number (include only if provided in resume)]  

[Current Date in Month DD, YYYY format]

[Hiring Manager's Name and Title (Optional, only if provided)]
[Company/Organization Name]  

Subject: Application for [Position Title]  
Dear [Hiring Manager or Director'Name],  

[PARAGRAPH 1: Express enthusiasm for the specific role and company. Briefly mention how you discovered the position and why you're interested in this particular company. Reference something specific about the company's work, values, or recent achievements.]

[PARAGRAPH 2: Highlight your most relevant qualifications and achievements that directly match the job requirements. Provide specific examples with measurable results when possible. Connect your past experiences directly to the needs outlined in the job description.]

[PARAGRAPH 3: Demonstrate your understanding of the company's goals/challenges and explain how your specific skills would help address them. Show evidence that you've researched the company beyond surface level.]

[CLOSING PARAGRAPH: Express interest in discussing your qualifications further in an interview. Thank them for considering your application and indicate your availability for next steps.]

Sincerely,

[Applicant's Full Name (must be in resume, if not given in resume say that it it not specified in resume)]
"""

async def generate_cover_letter(username,job_description,hiring_manager = "Hiring Manager",company_name = ""):
    resume_context = await return_context_from_faiss_vectorstore(username)
    cover_letter_prompt = ChatPromptTemplate.from_template(
        """
        Resume Information:
        {resume_context}
        
        Job Description:
        {job_description}
        
        Hiring Manager: {hiring_manager}
        Company Name: {company_name}
        
        {base_prompt}
        """
    )
    cover_letter_chain = cover_letter_prompt|llm|StrOutputParser()

    cover_letter = await cover_letter_chain.ainvoke({
        "resume_context": resume_context,
        "job_description": job_description,
        "hiring_manager": hiring_manager,
        "company_name": company_name,
        "base_prompt": base_prompt
    })
    return cover_letter


