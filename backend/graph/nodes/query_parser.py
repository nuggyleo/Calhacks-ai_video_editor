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
    Parses the structured query from the chatbot and routes to the next node.
    """
    parsed_query = state.get("parsed_query")
    if not parsed_query or "type" not in parsed_query:
        # If parsing failed or the format is wrong, end the graph gracefully.
        state["error"] = "Invalid or missing parsed query from chatbot."
        state["result"] = {"message": "Sorry, I couldn't understand the request structure."}
        return state

    query_type = parsed_query.get("type")

    # Route based on the 'type' field from the chatbot's JSON output.
    if query_type == "question":
        state["next_node"] = "answer_question"
    elif query_type == "edit":
        state["next_node"] = "execute_edit"
    else:
        # Handle unknown types
        state["error"] = f"Unknown query type: {query_type}"
        state["result"] = {"message": f"Sorry, I don't know how to handle a '{query_type}' request."}
        # In a real scenario, you might want a default fallback or end node.
        # For now, we can route to answer_question to explain the error.
        state["next_node"] = "answer_question"

    return state
