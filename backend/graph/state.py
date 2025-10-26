from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langgraph.graph.message import add_messages

class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        messages: The conversation history.
        query: The user's query.
        media_bin: A dictionary mapping unique IDs to video file paths.
        active_video_id: The ID of the video currently being edited.
        video_description: AI-generated description of the video content.
        parsed_query: The parsed result from the chatbot.
        parsed_actions: List[str]  # New field for natural language actions
        output_files: List[str]    # New field for multiple output files
        result: The result of the execution.
        error: Any error that occurred.
    """
    messages: Annotated[List[Any], add_messages]
    query: str
    media_bin: Dict[str, str]
    active_video_id: Optional[str]
    video_description: Optional[str]
    parsed_query: Dict[str, Any]
    parsed_actions: List[str]  # New field for natural language actions
    output_files: List[str]    # New field for multiple output files
    result: Optional[Dict[str, Any]]
    error: Optional[str]
