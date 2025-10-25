# This file defines the main langgraph graph.
# It imports the nodes from the 'nodes' directory and connects them to form a graph.
# The graph defines the flow of control and data between the nodes.

from langgraph.graph import StateGraph, END
from backend.graph.state import GraphState
from backend.graph.nodes.query_parser import query_parser
from backend.graph.nodes.answer_question import answer_question
from backend.graph.nodes.video_parser import video_parser
from backend.graph.nodes.dispatch_tasks import dispatch_tasks

def entry_point_router(state: GraphState):
    """
    Routes to the appropriate starting node based on the initial state.
    """
    if "video_path" in state and state["video_path"]:
        return "video_parser"
    elif "query" in state and state["query"]:
        return "query_parser"
    else:
        return END

def query_router(state: GraphState):
    """
    Routes to the next node based on the 'next_node' attribute in the state.
    """
    return state["next_node"]

# Define the graph
workflow = StateGraph(GraphState)

# Add the nodes
workflow.add_node("query_parser", query_parser)
workflow.add_node("answer_question", answer_question)
workflow.add_node("video_parser", video_parser)
workflow.add_node("dispatch_tasks", dispatch_tasks)


# Set the entry point router
workflow.set_entry_point("entry_point_router")

# Add the conditional edge from the entry point
workflow.add_conditional_edges(
    "entry_point_router",
    entry_point_router,
    {
        "video_parser": "video_parser",
        "query_parser": "query_parser",
    },
)

# Add edges from the parsers
workflow.add_edge("video_parser", "answer_question")

# Add the conditional edge from the query parser
workflow.add_conditional_edges(
    "query_parser",
    query_router,
    {
        "answer_question": "answer_question",
        "dispatch_tasks": "dispatch_tasks",
    },
)


# Add edges from the other nodes to the end
workflow.add_edge("answer_question", END)
workflow.add_edge("dispatch_tasks", END)

# Compile the graph
app = workflow.compile()
