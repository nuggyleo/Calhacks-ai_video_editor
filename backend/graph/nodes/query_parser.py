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
    Parses the user's query to determine if it's a question or an edit request.

    Args:
        state: The current graph state.

    Returns:
        The updated graph state.
    """
    query = state["query"]

    system_prompt = """
    You are an intelligent video editing assistant. Your task is to parse the user's query
    and determine if it is a question about the video or a request to edit the video.

    If the query is a question, classify it as 'question' and extract the question.
    Example: "What is this video about?" -> {"type": "question", "data": {"question": "What is this video about?"}}

    If the query is an edit request, classify it as 'edit' and extract the edit actions as a list of JSON objects.
    Each action should have an 'action' type and relevant parameters.
    Supported actions: 'cut', 'trim', 'add_text', 'speed_up', 'slow_down'.
    Example: "Cut the video from 10s to 20s and add 'Hello' at 5s" ->
    {"type": "edit", "data": [
        {"action": "cut", "start_time": 10, "end_time": 20},
        {"action": "add_text", "start_time": 5, "description": "Hello"}
    ]}

    Respond with a single JSON object that conforms to the following Pydantic schema:
    class EditAction(BaseModel):
        action: str
        start_time: float = None
        end_time: float = None
        description: str = None

    class Question(BaseModel):
        question: str

    class ParsedQuery(BaseModel):
        type: Literal["question", "edit"]
        data: Union[Question, List[EditAction]]
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        response_format={"type": "json_object"},
    )

    parsed_json = json.loads(response.choices[0].message.content)
    parsed_query = ParsedQuery(**parsed_json)

    if parsed_query.type == "question":
        state["next_node"] = "answer_question"
    else:
        state["next_node"] = "execute_edit"
    
    state["parsed_query"] = parsed_query.model_dump()

    return state
