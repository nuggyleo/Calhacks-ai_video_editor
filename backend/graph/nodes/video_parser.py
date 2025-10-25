# This node is responsible for parsing the video.
# It takes the video as input and extracts the text content from it.
# The text content can be obtained through speech-to-text or other analysis.

import subprocess
import json
from backend.graph.state import GraphState
from backend.ai_services.vision import analyze_video_content

def get_video_analysis(video_path: str) -> str:
    """
    Analyzes the visual content of a video and returns a summary.

    Args:
        video_path: The path to the video file.

    Returns:
        A string containing the video's content summary.
    """
    print("Generating video content analysis...")
    content_summary = analyze_video_content(video_path)
    return f"**Video Content Summary:**\n\n{content_summary}"


def video_parser(state: GraphState):
    """
    Parses the video to extract a content summary.
    
    Args:
        state: The current graph state containing the video path.
        
    Returns:
        The updated graph state with video metadata.
    """
    
    video_path = state.get("video_path")
    
    if not video_path:
        return {**state, "error": "No video path provided for analysis."}
        
    analysis_text = get_video_analysis(video_path)
    
    metadata = {
        "analysis": analysis_text,
    }
    
    return {
        **state,
        "video_metadata": metadata
    }
