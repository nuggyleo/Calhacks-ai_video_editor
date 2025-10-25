import os
import base64
import tempfile
from pathlib import Path
from openai import OpenAI
from moviepy.editor import VideoFileClip
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def analyze_video_content(video_path: str, num_frames: int = 5) -> str:
    """
    Analyzes the content of a video by extracting key frames and using a vision model.

    Args:
        video_path: The path to the video file.
        num_frames: The number of frames to extract for analysis.

    Returns:
        A descriptive summary of the video's content.
    """
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    try:
        # Create a temporary directory to store frames
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            clip = VideoFileClip(video_path)
            
            # Extract frames at evenly spaced intervals
            duration = clip.duration
            frame_paths = []
            for i in range(num_frames):
                timestamp = (i + 1) * duration / (num_frames + 1)
                frame_path = temp_path / f"frame_{i+1}.jpg"
                clip.save_frame(frame_path, t=timestamp)
                frame_paths.append(frame_path)
            
            # Encode frames to base64
            base64_frames = []
            for frame_path in frame_paths:
                with open(frame_path, "rb") as image_file:
                    base64_frames.append(base64.b64encode(image_file.read()).decode("utf-8"))
        
        # Create the prompt for the vision model
        prompt_messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "These are frames from a video. Please describe the content of the video based on these frames. Provide a short, one-paragraph summary.",
                    },
                    *map(lambda x: {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{x}"}}, base64_frames),
                ],
            },
        ]
        
        # Call the vision model
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=prompt_messages,
            max_tokens=200,
        )
        
        return response.choices[0].message.content

    except Exception as e:
        print(f"❌ Error during AI video content analysis: {e}")
        return "Could not generate a content summary for the video."
    finally:
        if 'clip' in locals():
            clip.close()
