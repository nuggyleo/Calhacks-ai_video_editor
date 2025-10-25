import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Literal, Union

from backend.graph.state import GraphState

load_dotenv()

class EditAction(BaseModel):
    action: str = Field(..., description="The type of edit action to perform.")
    start_time: float = Field(None, description="Start time for the edit in seconds.")
    end_time: float = Field(None, description="End time for the edit in seconds.")
    description: str = Field(None, description="Description of the edit.")

class Question(BaseModel):
    question: str = Field(..., description="The user's question about the video.")

class ParsedQuery(BaseModel):
    type: Literal["question", "edit"]
    data: Union[Question, List[EditAction]]

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def query_parser(state: GraphState):
    """
    This node is now a pass-through. The main routing logic is handled by the
    pre_analysis_router and the chatbot's tool_choice. This node remains
    to maintain the graph structure but performs no complex operations.
    It primarily prepares the state for the answer_question node.
    """
    # The 'parsed_query' from the chatbot is already in the correct format.
    # We just ensure the state is passed along correctly.
    print("--- PASSING THROUGH QUERY PARSER ---")
    
    # The primary purpose is now to set 'next_node' for the final step,
    # as the main routing happens before this. We can infer the next step
    # from the structure of parsed_query.
    if "question" in state.get("parsed_query", {}).get("data", {}):
         state["next_node"] = "answer_question"
    
    return state
