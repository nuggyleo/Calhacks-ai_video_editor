# This file defines the main langgraph graph.
# It imports the nodes from the 'nodes' directory and connects them to form a graph.
# The graph defines the flow of control and data between the nodes.

from langgraph.graph import StateGraph, END
from backend.graph.state import GraphState
from backend.graph.nodes.query_parser import query_parser
from backend.graph.nodes.answer_question import answer_question
from backend.graph.nodes.video_parser import video_parser
from backend.graph.nodes.dispatch_tasks import dispatch_tasks
from backend.graph.nodes.execute_edit import execute_edit
from backend.graph.nodes.chatbot import chatbot

def entry_point_router(state: GraphState):
    """
    Routes to the appropriate starting node based on the initial state.
    """
    return "chatbot"

def query_router(state: GraphState):
    """
    Routes to the next node based on the 'next_node' attribute in the state.
    """
    if state["next_node"] == "continue_chat":
        return "chatbot"
    else:
        return state["next_node"]

# Define the graph
workflow = StateGraph(GraphState)

# Add the nodes
workflow.add_node("chatbot", chatbot)
workflow.add_node("query_parser", query_parser)
workflow.add_node("answer_question", answer_question)
workflow.add_node("video_parser", video_parser)
workflow.add_node("dispatch_tasks", dispatch_tasks)
workflow.add_node("execute_edit", execute_edit)

# Set the entry point router
workflow.set_entry_point("entry_point_router")

# Add the chatbot entry point
workflow.add_edge("chatbot", "query_parser")

# Add the conditional edge from the query parser
workflow.add_conditional_edges(
    "query_parser",
    query_router,
    {
        "answer_question": "answer_question",
        "dispatch_tasks": "execute_edit",
        "continue_chat": "chatbot",
    },
)

# Add edges from the other nodes back to the chatbot
workflow.add_edge("answer_question", "chatbot")
workflow.add_edge("execute_edit", "chatbot")

# Compile the graph
app = workflow.compile()
