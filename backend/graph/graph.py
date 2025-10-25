# This file defines the main langgraph graph.
# It imports the nodes from the 'nodes' directory and connects them to form a graph.
# The graph defines the flow of control and data between the nodes.

from langgraph.graph import StateGraph, END
from backend.graph.state import GraphState
from backend.graph.nodes.query_parser import query_parser
from backend.graph.nodes.answer_question import answer_question
from backend.graph.nodes.execute_edit import execute_edit
from backend.graph.nodes.chatbot import chatbot
from backend.graph.nodes.vision_analyzer import vision_analyzer_node


def should_analyze_vision(state: GraphState):
    """
    Determines whether to run the vision analysis based on the presence of a video description.
    """
    if state.get("video_description"):
        print("--- SKIPPING VISION ANALYSIS (DESCRIPTION ALREADY EXISTS) ---")
        return "query_parser"
    else:
        print("--- ROUTING TO VISION ANALYSIS (NO DESCRIPTION) ---")
        return "vision_analyzer"


def query_router(state: GraphState):
    """
    Routes to the next node based on the 'type' field from the chatbot's JSON output.
    """
    next_node = state.get("next_node")
    if next_node == "continue_chat":
        return "chatbot"
    elif next_node == "dispatch_tasks": # 'dispatch_tasks' is the old name, routing to execute_edit
        return "execute_edit"
    else:
        return next_node # e.g., 'answer_question'

# Define the graph
workflow = StateGraph(GraphState)

# Add the nodes
workflow.add_node("chatbot", chatbot)
workflow.add_node("query_parser", query_parser)
workflow.add_node("answer_question", answer_question)
workflow.add_node("execute_edit", execute_edit)
workflow.add_node("vision_analyzer", vision_analyzer_node)

# Set the entry point
workflow.set_entry_point("chatbot")

# After the chatbot, decide whether to analyze the video content.
workflow.add_conditional_edges(
    "chatbot",
    should_analyze_vision,
    {
        "vision_analyzer": "vision_analyzer",
        "query_parser": "query_parser",
    },
)

# After analyzing, the enriched state goes to the query parser.
workflow.add_edge("vision_analyzer", "query_parser")

# From the query parser, route to the appropriate tool.
workflow.add_conditional_edges(
    "query_parser",
    query_router,
    {
        "answer_question": "answer_question",
        "execute_edit": "execute_edit",
        "continue_chat": "chatbot",
    },
)

# After a tool is used, the conversation loops back to the chatbot.
workflow.add_edge("answer_question", "chatbot")
workflow.add_edge("execute_edit", "chatbot")

# Compile the graph
app = workflow.compile()
