from linkedin.crawler.linkedIn_crawler import LinkedIn
from helper.response import Success, Error
import PyPDF2
import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing_extensions import TypedDict
import json
from typing import List


load_dotenv()
GEMINI_AI = os.getenv('GEMINI_AI')
UPLOAD_FOLDER = "./cv"

class Recipe(TypedDict):
    username: str
    skills: List[str]

async def getJobDetail(url: str) -> None:
    linkedin_instance = LinkedIn()
    job_id = await linkedin_instance.handleGetJobDetailFromUrl(url)
    return Success("GET_JOB_DETAIL", job_id)

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        extracted_text = ""
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text
        return extracted_text

async def generateSkillFromCV(uid):
    genai.configure(api_key=GEMINI_AI)
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    prompt = "Generate name, and skill of this cv"
    file_path = os.path.join(UPLOAD_FOLDER, f"{uid}.pdf")
    sample_file_2 = extract_text_from_pdf(file_path)
    response = model.generate_content([prompt, sample_file_2],
                    generation_config=genai.GenerationConfig(
                    response_mime_type="application/json", response_schema=Recipe
                ),)
    response_data = json.loads(response.text)
    return Success("Generate skill success", {"data": response_data})


async def generateSkillFromStr(str):
    genai.configure(api_key=GEMINI_AI)
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    prompt = f"Generate name, and skill of this cv form this text: '{str}'"
    response = model.generate_content([prompt],
                    generation_config=genai.GenerationConfig(
                    response_mime_type="application/json", response_schema=Recipe
                ),)
    response_data = json.loads(response.text)
    return response_data
