import os
import json
from typing import List, Dict, Any
from pathlib import Path

from backend.graph.state import GraphState
from backend.video_engine.editing.clips import split_video, concatenate_videos
from backend.video_engine.editing.effects import apply_filter, add_subtitle
from backend.video_engine.editing.audio import set_audio
from backend.video_engine.editing.export import export_video
from backend.ai_services.filter_mapper import map_description_to_filter

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
    parsed_query = state.get("parsed_query")

    if not video_path or not parsed_query:
        return {**state, "error": "Missing video path or parsed query."}
    
    try:
        # The 'data' from the parsed query should be a list of edit actions
        edit_data = parsed_query.get("data")
        
        # Ensure edit_data is a list
        if not isinstance(edit_data, list):
            edit_data = [edit_data]
        
        # Start with the original video
        clip = VideoFileClip(video_path)
        
        # Process each edit action in sequence
        for action in edit_data:
            action_type = action.get("action")
            
            if action_type == "trim" or action_type == "cut":
                # Trim the video from start_time to end_time
                start_time = action.get("start_time")
                end_time = action.get("end_time")

                # Sanitize inputs from the LLM. It might send 'end' as a string.
                if end_time == 'end' or end_time is None:
                    end_time = clip.duration
                
                # Default start time to the beginning if not provided.
                if start_time is None:
                    start_time = 0

                # Ensure times are numbers before proceeding
                try:
                    final_start = float(start_time)
                    final_end = float(end_time)
                except (ValueError, TypeError):
                    raise ValueError("Invalid start or end time provided by the model.")

                clip = clip.subclip(final_start, final_end)
                
                print(f"✅ Trimmed video from {final_start}s to {final_end}s")
            
            elif action_type == "add_text":
                # Add text/subtitle to the video
                text = action.get("description", "")
                start_time = action.get("start_time", 0)
                duration = action.get("duration", 3)
                clip = add_subtitle(clip, text, start_time, duration)
                print(f"✅ Added text: '{text}' at {start_time}s")
            
            elif action_type == "add_filter":
                # Apply a filter to the video
                filter_description = action.get("description", "")
                
                # Map the natural language description to a moviepy filter
                filter_info = map_description_to_filter(filter_description)
                filter_name = filter_info.get("filter_name")
                parameters = filter_info.get("parameters", {})
                
                # Apply the filter
                clip = apply_filter(clip, filter_name, **parameters)
                print(f"✅ Applied filter: {filter_name} with parameters {parameters}")
            
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
        
        # Define the output directory relative to the project root
        # Assumes this script is in backend/graph/nodes
        output_dir = Path(__file__).parent.parent.parent.parent / "outputs"
        output_dir.mkdir(exist_ok=True, parents=True)

        # Create a unique output path
        original_filename = Path(video_path).name
        output_path = str(output_dir / f"edited_{original_filename}")
        
        # Export the final edited video
        export_video(clip, output_path)
        
        return {
            "result": {
                "status": "completed",
                "message": f"Video edited successfully! You can find it at: {output_path}",
                "output_path": output_path
            }
        }
    
    except Exception as e:
        return {
            **state,
            "error": str(e),
            "result": {
                "status": "error",
                "message": f"An error occurred during video editing: {str(e)}"
            }
        }
