from backend.graph.state import GraphState
from backend.ai_services.vision import analyze_video_content

def vision_analyzer_node(state: GraphState):
    """
    Analyzes the video content using a vision model and updates the state.
    """
    print("---ANALYZING VIDEO CONTENT WITH VISION MODEL---")
    
    # Get the active video ID and media bin
    active_video_id = state.get("active_video_id")
    media_bin = state.get("media_bin", {})
    
    # Get the video path from media_bin using active_video_id
    video_path = media_bin.get(active_video_id)
    
    if not video_path:
        print(f"❌ Error: No video path found for active_video_id '{active_video_id}'")
        print(f"Available videos in media_bin: {list(media_bin.keys())}")
        return {**state, "error": f"Video path not found for ID '{active_video_id}'."}
    
    print(f"Analyzing video: {video_path}")

    try:
        # Call the vision analysis function
        description = analyze_video_content(video_path)
        print(f"✅ Vision analysis complete. Description: {description[:100]}...")
        
        # Update the state with the new description
        return {**state, "video_description": description}

    except Exception as e:
        print(f"❌ Error during vision analysis: {e}")
        import traceback
        traceback.print_exc()
        return {**state, "error": f"Failed to analyze video content: {e}"}
