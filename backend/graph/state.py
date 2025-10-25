from typing import TypedDict, List, Dict, Any

class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        query: user's query
        video_path: path to the video file
        parsed_query: dictionary containing the parsed result from the query_parser
        next_node: the next node to route to
    """
    query: str
    video_path: str
    parsed_query: Dict[str, Any]
    next_node: str
