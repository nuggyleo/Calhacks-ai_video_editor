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
    Parses the user's query to determine if it's a question or an edit request
    using a structured output model.
    """
    query = state["query"]
    print(f"---PARSING QUERY: '{query}'---")

    # Initialize the model
    model = ChatOpenAI(model="gpt-4o", temperature=0, api_key=os.environ.get("OPENAI_API_KEY"))
    
    # Create a structured output model
    structured_llm = model.with_structured_output(ParsedQuery)

    system_prompt = """You are an intelligent video editing assistant. Your task is to parse the user's query and determine if it is a question about the video or a request to edit the video. Extract the information into the structured format required."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{query}")
    ])
    
    # Create the chain and invoke it
    chain = prompt | structured_llm
    parsed_query = chain.invoke({"query": query})

    if parsed_query.type == "question":
        print("Query classified as a question.")
        state["next_node"] = "answer_question"
    else:
        print(f"Query classified as an edit. Actions: {[action.action for action in parsed_query.data]}")
        state["next_node"] = "execute_edit"
    
    state["parsed_query"] = parsed_query.dict()

    return state
