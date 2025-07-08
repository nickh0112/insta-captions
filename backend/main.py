#!/usr/bin/env python3
"""
FastAPI Backend for Instagram Reels Transcript Extractor
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import uuid
import os
import shutil
import json
import asyncio
from pathlib import Path
import subprocess
import tempfile
import zipfile
from datetime import datetime

app = FastAPI(title="Instagram Reels Transcript Extractor", version="1.0.0")

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Job storage (in production, use Redis or a database)
jobs: Dict[str, Dict] = {}

# Models
class URLSubmission(BaseModel):
    urls: List[str]

class JobStatus(BaseModel):
    job_id: str
    state: str  # "pending", "running", "completed", "failed"
    progress: float
    message: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None

class JobResponse(BaseModel):
    job_id: str
    message: str

# Endpoints
@app.get("/")
async def root():
    return {"message": "Instagram Reels Transcript Extractor API"}

@app.post("/submit", response_model=JobResponse)
async def submit_urls(submission: URLSubmission, background_tasks: BackgroundTasks):
    """Submit Instagram URLs for processing"""
    if not submission.urls:
        raise HTTPException(status_code=400, detail="No URLs provided")
    
    job_id = str(uuid.uuid4())
    
    # Initialize job
    jobs[job_id] = {
        "job_id": job_id,
        "state": "pending",
        "progress": 0.0,
        "message": "Job created",
        "urls": submission.urls,
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
        "workspace": None
    }
    
    # Start background processing
    background_tasks.add_task(process_urls, job_id, submission.urls)
    
    return JobResponse(job_id=job_id, message="Job submitted successfully")

@app.get("/status/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get job status"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    return JobStatus(
        job_id=job["job_id"],
        state=job["state"],
        progress=job["progress"],
        message=job["message"],
        created_at=job["created_at"],
        completed_at=job.get("completed_at")
    )

@app.get("/result/{job_id}")
async def download_result(job_id: str):
    """Download the transcript ZIP file"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if job["state"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    workspace = job.get("workspace")
    if not workspace or not os.path.exists(workspace):
        raise HTTPException(status_code=404, detail="Results not found")
    
    # Create ZIP file
    zip_path = f"{workspace}/transcripts.zip"
    create_zip_file(f"{workspace}/subs", zip_path)
    
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="ZIP file not found")
    
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"transcripts_{job_id}.zip"
    )

@app.get("/jobs")
async def list_jobs():
    """List all jobs"""
    return {"jobs": list(jobs.values())}

@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job and its files"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    workspace = job.get("workspace")
    
    # Clean up workspace
    if workspace and os.path.exists(workspace):
        shutil.rmtree(workspace)
    
    # Remove from jobs
    del jobs[job_id]
    
    return {"message": "Job deleted successfully"}

# Background processing function
async def process_urls(job_id: str, urls: List[str]):
    """Process Instagram URLs in the background"""
    try:
        # Update job status
        jobs[job_id]["state"] = "running"
        jobs[job_id]["message"] = "Setting up workspace..."
        jobs[job_id]["progress"] = 0.1
        
        # Create temporary workspace
        workspace = tempfile.mkdtemp(prefix=f"job_{job_id}_")
        jobs[job_id]["workspace"] = workspace
        
        # Create required directories
        os.makedirs(f"{workspace}/subs", exist_ok=True)
        os.makedirs(f"{workspace}/tmp", exist_ok=True)
        
        # Write URLs to reels.txt
        with open(f"{workspace}/reels.txt", "w") as f:
            for url in urls:
                # Split on whitespace to handle pasted URLs separated by spaces or newlines
                for u in url.split():
                    if u.strip():
                        f.write(f"{u.strip()}\n")
        
        jobs[job_id]["message"] = "Extracting existing captions..."
        jobs[job_id]["progress"] = 0.3
        
        # Run scrape_subs.py
        await run_scrape_subs(workspace)
        
        jobs[job_id]["message"] = "Processing with Whisper..."
        jobs[job_id]["progress"] = 0.6
        
        # Run fill_gaps.py
        await run_fill_gaps(workspace)
        
        jobs[job_id]["message"] = "Finalizing results..."
        jobs[job_id]["progress"] = 0.9
        
        # Check if any transcripts were created
        subs_dir = Path(f"{workspace}/subs")
        txt_files = list(subs_dir.glob("*.txt"))
        
        if not txt_files:
            jobs[job_id]["state"] = "failed"
            jobs[job_id]["message"] = "No transcripts were generated"
            return
        
        # Job completed successfully
        jobs[job_id]["state"] = "completed"
        jobs[job_id]["progress"] = 1.0
        jobs[job_id]["message"] = f"Successfully processed {len(txt_files)} transcripts"
        jobs[job_id]["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        jobs[job_id]["state"] = "failed"
        jobs[job_id]["message"] = f"Error: {str(e)}"
        jobs[job_id]["progress"] = 0.0

async def run_scrape_subs(workspace: str):
    """Run the scrape_subs.py script"""
    # Import and run the function directly
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    
    from scrape_subs import run_batch
    
    # Change to workspace directory
    original_cwd = os.getcwd()
    os.chdir(workspace)
    
    try:
        run_batch("reels.txt")
    finally:
        os.chdir(original_cwd)

async def run_fill_gaps(workspace: str):
    """Run the fill_gaps.py script"""
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    
    from fill_gaps import main as fill_gaps_main
    
    # Change to workspace directory
    original_cwd = os.getcwd()
    os.chdir(workspace)
    
    try:
        fill_gaps_main()
    finally:
        os.chdir(original_cwd)

def create_zip_file(source_dir: str, zip_path: str):
    """Create a ZIP file from the source directory"""
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        source_path = Path(source_dir)
        for file_path in source_path.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(source_path)
                zipf.write(file_path, arcname)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 