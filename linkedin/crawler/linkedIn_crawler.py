import os
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import google.generativeai as genai
from typing_extensions import TypedDict
import json
from typing import List
from dotenv import load_dotenv

load_dotenv()

current_directory = os.path.dirname(os.path.abspath(__file__))
COOKIES_PATH = os.path.join(current_directory, '../cookies/linkedin_cookies.json')
GEMINI_AI = os.getenv('GEMINI_AI')

class Recipe(TypedDict):
    skills: List[str]

class LinkedIn:
    def __init__(self):
        self.source = "linkedIn"
        self.listJobUrl="https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?"
        self.jobDetailUrl="https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{}"
        self.cookiesPath= COOKIES_PATH

    def load_cookies(self):
        with open(self.cookiesPath, 'r') as f:
            cookies = json.load(f)
            return {cookie['name']: cookie['value'] for cookie in cookies}

    async def getJobDetail(self, jobId):
        session = requests.Session()
        session.cookies.update(self.load_cookies())
        url = self.jobDetailUrl.format(jobId)
        response = session.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')

        job_url = ""
        job_title = ""
        company_url = ""
        company_img_url = ""
        location_value = ""
        description_value = ""
        description_span = ""

        job_link = soup.find('a', {'data-tracking-control-name': 'public_jobs_topcard-title'})
        if job_link:
            job_url = job_link['href']
            job_title = job_link.find('h2').text.strip()

        company_link = soup.find('a', {'data-tracking-control-name': 'public_jobs_topcard_logo'})
        if company_link:
            company_url = job_link['href']
            img_tag = company_link.find('img')
            if img_tag:
                company_img_url = img_tag['data-delayed-url']

        location_span = soup.find('span', class_='topcard__flavor topcard__flavor--bullet')
        if location_span:
            location_value = location_span.text.strip()

        description_span = soup.find('div', class_='description__text description__text--rich')
        if description_span:
            for button in soup.find_all('button'):
                button.decompose()
            description_value = description_span.text.strip()

        skills = await self.generateSkillFromStr(description_value)

        payload = {
            "job_url": job_url,
            "job_title": job_title,
            "company_url": company_url,
            "company_img_url": company_img_url,
            "location": location_value,
            "description": description_value,
            "description_raw": str(description_span),
            "source": self.source,
            "jobId": jobId,
            "skills": skills
        }
        return payload


    def print_source(self, location, keywords):
        parameters = {
            "keywords": "NodeJS",
            "location": "Vietnam",
            "start": 0,
            "f_TPR": "r2592000",
        }
        url = f"{(self.listJobUrl + urlencode(parameters))}"
        session = requests.Session()
        session.cookies.update(self.load_cookies())
        response = session.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')
        urn_values = []
        job_details_list = []
        for tag in soup.find_all(attrs={"data-entity-urn": True}):
            urn = tag['data-entity-urn']
            value = urn.split(':')[-1]
            urn_values.append(value)
        for job_id in urn_values:
            job_detail = self.getJobDetail(job_id)
            job_details_list.append(job_detail)
        with open("job_details.json", 'w', encoding='utf-8') as f:
            json.dump(job_details_list, f, ensure_ascii=False, indent=4)

    async def handleGetJobDetailFromUrl(self, url):
        jobId = self.getJobId(url)
        jobData = await self.getJobDetail(jobId)
        return jobData

    def getJobId(self, url):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        query_params = parse_qs(parsed_url.query)
        if "currentJobId" in query_params:
            return query_params["currentJobId"][0]
        path_parts = parsed_url.path.strip("/").split("-")
        if path_parts[-1].isdigit():
            return path_parts[-1]
        return None

    async def generateSkillFromStr(self, str):
        genai.configure(api_key=GEMINI_AI)
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        prompt = f"Generate name, and skill of this cv form this text: '{str}'"
        response = model.generate_content([prompt],
                    generation_config=genai.GenerationConfig(
                    response_mime_type="application/json", response_schema=Recipe
                ),)
        response_data = json.loads(response.text)
        return response_data

