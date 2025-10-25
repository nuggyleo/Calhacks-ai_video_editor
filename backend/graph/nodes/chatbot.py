from typing import List
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from backend.graph.state import GraphState

def chatbot(state: GraphState):
    """
    Simulates a chatbot that interacts with the user.
    
    This node will be part of a loop, allowing for continuous conversation.
    """
    
    # Initialize the chatbot model
    model = ChatOpenAI(temperature=0, streaming=True)
    
    # Get the user's query from the state
    query = state.get("query")
    
    # If the user's query is "exit", end the conversation
    if query and query.lower() == "exit":
        return END
    
    # Create a message history
    messages: List[BaseMessage] = [
        HumanMessage(content=query)
    ]
    
    # Get the AI's response
    response = model.invoke(messages)
    
    # Update the state with the chatbot's response
    return {
        **state,
        "result": {
            "status": "continue",
            "message": response.content
        }
    }
