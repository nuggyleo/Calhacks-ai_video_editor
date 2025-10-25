
# This is the main entry point for the FastAPI application.
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uuid
import tempfile
import json
from pydantic import BaseModel
import subprocess
import base64
import os

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

# Use the system's temporary directory which is always writable
UPLOAD_DIR = Path(tempfile.gettempdir()) / "calhacks_uploads"
print(f"--- Using temporary directory for uploads: {UPLOAD_DIR} ---")

# Create the directory on startup
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)

# FFmpeg path
FFMPEG_PATH = r'C:\Program Files\JianyingPro\Apps\5.7.0.11527\ffmpeg.exe'

def get_video_analysis_placeholder(filename: str) -> str:
    """
    Returns a detailed video analysis placeholder.
    This is used for testing the frontend UI before real ffmpeg integration.
    """
    return f"""This video appears to be a professional recording with clear audio and visual content. 

**Scene 1 - Opening (0:00-0:05):** The video begins with an introduction sequence, establishing the setting and context.

**Scene 2 - Main Content (0:05-0:20):** The primary subject matter is presented with detailed explanations. Multiple visual elements support the narrative.

**Scene 3 - Details (0:20-0:30):** Specific examples and close-up details are shown to illustrate key points.

**Scene 4 - Conclusion (0:30-0:35):** The video concludes with a summary and call-to-action.

**Overall Quality:** The video is well-produced with consistent lighting, good audio quality, and professional editing. Suitable for further editing and effects enhancement."""

# Define request models
class EditCommandRequest(BaseModel):
    """Request model for video editing commands"""
    video_id: str
    video_url: str
    command: str
    video_description: str = ""  # Optional: AI analysis of video content

# Define routes
@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Video Editor Backend!"}

@app.post("/api/upload")
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
        
        # Generate analysis (placeholder for now - using real ffmpeg later)
        print(f"Generating video analysis for: {file_path}")
        description = get_video_analysis_placeholder(file.filename or "video.mp4")
        print("Video analysis generated")
        
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
        print(f"Video ID: {request.video_id}")
        print(f"Video URL: {request.video_url}")
        print(f"Command: {request.command}")
        print(f"Video Description: {request.video_description}")
        
        # Import the graph
        from backend.graph.graph import app as graph
        
        # Find the video file path from the URL
        # The URL is like "/uploads/uuid.mp4"
        # We need to map it back to the actual file path
        from pathlib import Path
        import tempfile
        
        # Extract filename from URL
        filename = request.video_url.split("/")[-1]
        file_path = str(Path(tempfile.gettempdir()) / "calhacks_uploads" / filename)
        
        # Run the graph with the user's command
        result = graph.invoke({
            "query": request.command,
            "video_path": file_path,
            "parsed_query": {},
            "next_node": "",
            "result": None,
            "error": None,
        })
        
        # Extract the result from the graph execution
        execution_result = result.get("result", {})
        execution_error = result.get("error")
        
        if execution_error:
            response = {
                "status": "error",
                "video_id": request.video_id,
                "command": request.command,
                "message": f"Error during video editing: {execution_error}",
                "request_id": str(uuid.uuid4())
            }
        else:
            response = {
                "status": "completed",
                "video_id": request.video_id,
                "command": request.command,
                "message": execution_result.get("message", "Video editing completed"),
                "output_path": execution_result.get("output_path"),
                "request_id": str(uuid.uuid4())
            }
        
        print(f"Response: {json.dumps(response, indent=2)}")
        return response
        
    except Exception as e:
        print(f"Edit error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
