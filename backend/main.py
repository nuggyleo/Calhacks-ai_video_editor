
import sys
from pathlib import Path

# --- Pillow/MoviePy Compatibility Hotfix ---
# Pillow 10.0.0+ removed the ANTIALIAS attribute, which moviepy still uses.
# This monkey-patches the Image module to restore it, pointing to the new equivalent.
try:
    from PIL import Image
    if not hasattr(Image, 'ANTIALIAS'):
        # Pillow > 10.0.0
        setattr(Image, 'ANTIALIAS', Image.Resampling.LANCZOS)
    if not hasattr(Image, 'AFFINE'):
        # Pillow > 10.0.0
        setattr(Image, 'AFFINE', Image.Transform.AFFINE)
except ImportError:
    pass # Pillow not installed
# --- End Hotfix ---

from typing import List, Dict

# --- Path Hotfix ---
# This code adds the project's root directory to the Python path.
# This ensures that modules can be imported using absolute paths (e.g., `from backend.graph...`)
# regardless of where the application is run from.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))
# --- End Path Hotfix ---

# This is the main entry point for the FastAPI application.

import os
import uuid
import tempfile
import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage

from backend.graph.graph import app as graph_app
from backend.graph.nodes.video_parser import get_video_analysis
from backend.database import models
from backend.database.database import engine
from backend.api import endpoints

models.Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Conversational Video Editor API",
    description="API to process video editing commands from natural language.",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router, prefix="/api")

# Use the system's temporary directory which is always writable
UPLOAD_DIR = Path(tempfile.gettempdir()) / "calhacks_uploads"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
print(f"--- Using temporary directory for uploads: {UPLOAD_DIR} ---")
print(f"--- Using output directory for edited videos: {OUTPUT_DIR} ---")

# Create the directories on startup
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# FFmpeg path
FFMPEG_PATH = r'C:\\Program Files\\JianyingPro\\Apps\\5.7.0.11527\\ffmpeg.exe'

class EditCommandRequest(BaseModel):
    """Request model for video editing commands"""
    active_video_id: str
    media_bin: Dict[str, str]
    command: str
    video_description: str = ""
    chat_history: List[Dict[str, str]] = []

# Define routes
@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Video Editor Backend!"}

@app.post("/api/upload", summary="Upload video file", description="Uploads a video file and returns its metadata.")
async def upload_video(file: UploadFile = File(...)):
    """Upload a video file and return its analysis"""
    try:
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename or "video.mp4").suffix
        safe_filename = f"{file_id}{file_extension}"
        file_path = UPLOAD_DIR / safe_filename
        
        # Save file
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        print(f"File uploaded: {safe_filename} ({len(content)} bytes)")
        
        # Generate analysis with ffprobe
        print(f"Generating basic video metadata for: {file_path}")
        description = get_video_analysis(str(file_path))
        print("Basic metadata generated")
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "url": f"/uploads/{safe_filename}",
            "size": len(content),
            "file_path": str(file_path),
            "description": description
        }
    except Exception as e:
        print(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-video")
async def analyze_video(request: dict):
    """
    Analyze video by extracting frames and using AI to understand content.
    Returns a description of the video that can be used as context for editing commands.
    """
    try:
        video_id = request.get("video_id")
        file_path = request.get("file_path")
        
        print(f"\n--- Analyzing video ---")
        print(f"Video ID: {video_id}")
        print(f"File path: {file_path}")
        
        # TODO: Implement video frame extraction using ffmpeg
        # Extract 3-5 key frames from the video
        # Use OpenAI Vision API or Claude Vision to analyze the frames
        # Generate a comprehensive description of video content
        
        # Placeholder response
        description = """[Video Analysis]
Scene 1: Introduction
Scene 2: Main content
Scene 3: Conclusion
Duration: Video frames extracted
Recommended effects: Transitions, color grading"""
        
        response = {
            "status": "completed",
            "video_id": video_id,
            "description": description,
            "frames_analyzed": 3,
            "message": "Video analysis complete"
        }
        
        print(f"Response: {json.dumps(response, indent=2)}")
        return response
        
    except Exception as e:
        print(f"Video analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/edit")
async def edit_video(request: EditCommandRequest):
    """
    Process a video editing command using the LangGraph system.
    Receives a natural language command with video context and processes it through the graph.
    """
    try:
        print(f"\n--- Processing edit command ---")
        print(f"Active Video ID: {request.active_video_id}")
        print(f"Command: {request.command}")
        
        # --- NEW: Reconstruct media_bin with server-side file paths ---
        reconstructed_media_bin = {}
        for video_id, video_url in request.media_bin.items():
            filename = Path(video_url).name
            
            # Check for the video in both the uploads and outputs directories
            video_path_in_uploads = UPLOAD_DIR / filename
            video_path_in_outputs = OUTPUT_DIR / filename
            
            if video_path_in_uploads.exists():
                reconstructed_media_bin[video_id] = str(video_path_in_uploads)
            elif video_path_in_outputs.exists():
                reconstructed_media_bin[video_id] = str(video_path_in_outputs)
            else:
                raise HTTPException(status_code=404, detail=f"Video file for ID '{video_id}' not found: {filename}")
        
        print(f"Reconstructed Media Bin for Backend: {reconstructed_media_bin}")

        # Construct the message history from the request
        messages = []
        for msg in request.chat_history:
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") == "assistant":
                messages.append(AIMessage(content=msg.get("content", "")))
        messages.append(HumanMessage(content=request.command))

        # Run the graph with the reconstructed, path-based media_bin
        initial_state = {
            "messages": messages,
            "query": request.command,
            "media_bin": reconstructed_media_bin,
            "active_video_id": request.active_video_id,
            "video_description": request.video_description,
        }
        
        result = graph_app.invoke(initial_state)
        
        # The final result is contained in the last message added by the graph.
        final_message = result.get("messages", [])[-1]
        message_content = final_message.content
        
        # Check if the final message contains a video output URL
        output_url = final_message.additional_kwargs.get("output_url", None)

        response = {
            "status": "completed",
            "video_id": request.active_video_id, # Use active_video_id from the request
            "command": request.command,
            "message": message_content,
            "output_url": output_url,
            "request_id": str(uuid.uuid4())
        }
        
        print(f"Response: {json.dumps(response, indent=2)}")
        return response
        
    except Exception as e:
        print(f"Edit error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")
