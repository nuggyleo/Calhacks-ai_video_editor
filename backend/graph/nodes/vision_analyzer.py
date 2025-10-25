from backend.graph.state import GraphState
from backend.ai_services.vision import analyze_video_content

def vision_analyzer_node(state: GraphState):
    """
    Analyzes the video content using a vision model and updates the state.
    """
    print("---ANALYZING VIDEO CONTENT WITH VISION MODEL---")
    video_path = state.get("video_path")
    if not video_path:
        print("❌ Error: Video path not found in state.")
        return {**state, "error": "Video path not found for analysis."}

    try:
        # Call the vision analysis function
        description = analyze_video_content(video_path)
        print(f"✅ Vision analysis complete. Description: {description[:100]}...")
        
        # Update the state with the new description
        return {**state, "video_description": description}

    except Exception as e:
        print(f"❌ Error during vision analysis: {e}")
        return {**state, "error": f"Failed to analyze video content: {e}"}
