from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from helper.response import Success, Error
from pydantic import BaseModel
from service.linkedin import getJobDetail, generateSkillFromCV
from linkedin.crawler.applyCv import LinkedInJobApplicationService
import os
import shutil
import uuid
import PyPDF2
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI( title = "ABM",
    redirect_slashes=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

class URLRequest(BaseModel):
    url: str

UPLOAD_FOLDER = "./cv"
CAPTURE_FOLDER = "./capture"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

job_application_service = LinkedInJobApplicationService()

class JobApplicationRequest(BaseModel):
    cv_id: str
    job_url: str

@app.get("/health")
async def healthChecker():
    return Success("API V1 is running", [])

@app.post("/get-job-detail")
async def api_print_url(request: URLRequest):
    return  await getJobDetail(request.url)

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    unique_filename = f"{uuid.uuid4()}.pdf"
    file_location = os.path.join(UPLOAD_FOLDER, unique_filename)

    try:

        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to upload file") from e

    return Success("File uploaded successfully", {"file_uid": unique_filename})

@app.get("/download/{pdf_id}")
async def download_pdf(pdf_id: str):
    file_path = os.path.join(UPLOAD_FOLDER, f"{pdf_id}.pdf")

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path, media_type="application/pdf", filename=f"{pdf_id}.pdf")

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    unique_filename = f"{uuid.uuid4()}.pdf"
    file_location = os.path.join(UPLOAD_FOLDER, unique_filename)

    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to upload file") from e

    return Success("File uploaded successfully", {"file_uid": unique_filename})

@app.get("/generate/skill/{pdf_id}")
async def download_pdf(pdf_id: str):
    return await generateSkillFromCV(pdf_id)


@app.get("/capture/{imgId}")
async def show_image(imgId: str):
    image_path = os.path.join(CAPTURE_FOLDER,  f"{imgId}.png")
    if not os.path.isfile(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    media_type = "image/jpeg"
    return FileResponse(image_path, media_type=media_type, headers={"Content-Disposition": "inline"})


@app.post("/apply-job")
async def apply_job(request: JobApplicationRequest):
    try:
        screenshot_uid = await job_application_service.apply_to_job(request.job_url, request.cv_id)
        if screenshot_uid:
            return {"status": "success", "screenshot_uid": screenshot_uid}
        else:
            # raise HTTPException(status_code=500, detail="Failed to complete the job application")
            return Error("Failed to complete the job application.", 500)
    except Exception as e:
        error_message = str(e)
        print(error_message)
        return Error(error_message, 500)