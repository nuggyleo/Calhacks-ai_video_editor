import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List, Literal, Union
from dotenv import load_dotenv

from backend.graph.state import GraphState

# Load environment variables from .env file
load_dotenv()

class EditAction(BaseModel):
    action: str = Field(..., description="The type of edit action to perform. Supported actions: 'cut', 'trim', 'add_text', 'speed_up', 'slow_down', 'add_filter', 'set_audio'.")
    start_time: float = Field(None, description="Start time for the edit in seconds.")
    end_time: float = Field(None, description="End time for the edit in seconds.")
    description: str = Field(None, description="Description of the edit (e.g., text content, filter name).")

class Question(BaseModel):
    question: str = Field(..., description="The user's question about the video.")

class ParsedQuery(BaseModel):
    """The parsed structure of the user's query."""
    type: Literal["question", "edit"] = Field(..., description="Is the query a 'question' or an 'edit' request?")
    data: Union[Question, List[EditAction]] = Field(..., description="The structured data from the query.")


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
