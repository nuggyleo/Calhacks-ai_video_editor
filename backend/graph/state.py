from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langgraph.graph.message import add_messages

class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        messages: The conversation history. This is managed by langgraph to append messages.
        query: user's query
        video_path: path to the video file
        video_description: AI-generated description of the video content
        parsed_query: dictionary containing the parsed result from the query_parser
        next_node: the next node to route to
        result: the result of the execution
        error: any error that occurred during execution
    """
    messages: Annotated[List[Any], add_messages]
    query: str
    video_path: str
    video_description: Optional[str]
    parsed_query: Dict[str, Any]
    next_node: str
    result: Optional[Dict[str, Any]]
    error: Optional[str]
