from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from helper.response import Success, Error
from pydantic import BaseModel
from service.linkedin import getJobDetail, generateSkillFromCV
import os
import shutil
import uuid
import PyPDF2

app = FastAPI()

class URLRequest(BaseModel):
    url: str

UPLOAD_FOLDER = "./cv"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.get("/health")
async def healthChecker():
    return Success("API V1 is running", [])

@app.post("/get-job-detail/")
async def api_print_url(request: URLRequest):
    return  await getJobDetail(request.url)

@app.post("/upload-pdf/")
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

@app.post("/upload-pdf/")
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

