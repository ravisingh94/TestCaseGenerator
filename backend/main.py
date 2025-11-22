from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import shutil
import os
import uuid
from backend.graph import app_graph
from backend.streaming import stream_test_case_generation

app = FastAPI(title="Requirement Test Case Generator", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    file_path: str
    feature_name: str
    test_case_limit: Optional[int] = None
    url: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Requirement Test Case Generator API is running"}

@app.get("/status")
async def status():
    return {"status": "ok"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return {"file_path": file_path, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate")
async def generate_test_cases(request: GenerateRequest):
    try:
        inputs = {
            "file_path": request.file_path,
            "feature_name": request.feature_name,
            # Initialize other state variables if needed, though TypedDict handles missing keys gracefully if not required
            "documents": [],
            "chunks": [],
            "retrieved_chunks": [],
            "generated_test_cases": [],
            "hallucination_errors": [],
            "final_output": {}
        }
        
        result = app_graph.invoke(inputs)
        return result["final_output"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-stream")
async def generate_test_cases_stream(request: GenerateRequest):
    """
    Streaming endpoint for progressive test case generation.
    Uses Server-Sent Events (SSE) to send test cases as they're generated.
    """
    return StreamingResponse(
        stream_test_case_generation(
            request.file_path, 
            request.feature_name, 
            request.test_case_limit,
            request.url
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
