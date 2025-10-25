import os
import json
from typing import List, Dict, Any
from pathlib import Path

from backend.graph.state import GraphState
from backend.video_engine.editing.clips import split_video, concatenate_videos
from backend.video_engine.editing.effects import apply_filter, add_subtitle
from backend.video_engine.editing.audio import set_audio
from backend.video_engine.editing.export import export_video

from moviepy.editor import VideoFileClip

def execute_edit(state: GraphState):
    """
    Executes the video edit operations based on the parsed query.
    
    Args:
        state: The current graph state containing the parsed edit actions.
        
    Returns:
        The updated graph state with execution results.
    """
    
    video_path = state.get("video_path")
    parsed_query = state.get("parsed_query", {})
    
    if not video_path or not os.path.exists(video_path):
        return {
            **state,
            "error": f"Video file not found: {video_path}",
            "result": None
        }
    
    try:
        # Extract the edit actions from the parsed query
        edit_data = parsed_query.get("data", [])
        if not isinstance(edit_data, list):
            edit_data = [edit_data]
        
        # Start with the original video
        clip = VideoFileClip(video_path)
        
        # Process each edit action in sequence
        for action in edit_data:
            action_type = action.get("action")
            
            if action_type == "trim" or action_type == "cut":
                # Trim the video from start_time to end_time
                start_time = action.get("start_time", 0)
                end_time = action.get("end_time", clip.duration)
                
                # Make sure to get a full clip object
                with VideoFileClip(video_path) as video:
                    clip = video.subclip(start_time, end_time)
                
                print(f"✅ Trimmed video from {start_time}s to {end_time}s")
            
            elif action_type == "add_text":
                # Add text/subtitle to the video
                text = action.get("description", "")
                start_time = action.get("start_time", 0)
                duration = action.get("duration", 3)
                clip = add_subtitle(clip, text, start_time, duration)
                print(f"✅ Added text: '{text}' at {start_time}s")
            
            elif action_type == "add_filter":
                # Apply a filter to the video
                filter_name = action.get("description", "")
                clip = apply_filter(clip, filter_name)
                print(f"✅ Applied filter: {filter_name}")
            
            elif action_type == "speed_up":
                # Speed up the video
                speed_factor = action.get("speed_factor", 1.5)
                clip = clip.speedx(speed_factor)
                print(f"✅ Sped up video by {speed_factor}x")
            
            elif action_type == "slow_down":
                # Slow down the video
                speed_factor = action.get("speed_factor", 0.5)
                clip = clip.speedx(speed_factor)
                print(f"✅ Slowed down video by {1/speed_factor}x")
            
            elif action_type == "set_audio":
                # Replace audio with a new audio file
                audio_path = action.get("audio_path", "")
                clip = set_audio(clip, audio_path)
                print(f"✅ Set audio to: {audio_path}")
        
        # Export the final edited video
        output_path = str(Path(video_path).parent / f"edited_{Path(video_path).name}")
        export_video(clip, output_path)
        
        return {
            **state,
            "result": {
                "status": "success",
                "output_path": output_path,
                "message": "Video editing completed successfully"
            },
            "error": None
        }
    
    except Exception as e:
        print(f"❌ Error during video editing: {str(e)}")
        return {
            **state,
            "error": str(e),
            "result": {
                "status": "error",
                "message": f"Error during video editing: {str(e)}"
            }
        }
