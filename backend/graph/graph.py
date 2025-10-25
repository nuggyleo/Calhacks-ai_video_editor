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


def pre_analysis_router(state: GraphState):
    """
    Routes to the correct tool based on the chatbot's initial analysis,
    bypassing vision analysis for direct edits.
    """
    tool_choice = state.get("parsed_query", {}).get("tool_choice")
    if tool_choice == "execute_edit":
        print("--- ROUTING DIRECTLY TO EXECUTE EDIT ---")
        return "execute_edit"
    elif tool_choice == "answer_question":
        print("--- ROUTING TO CONTEXTUAL ANALYSIS ---")
        return "should_analyze_vision"
    else:
        # Fallback or error handling
        print(f"--- UNKNOWN TOOL CHOICE: {tool_choice} ---")
        return "answer_question" # Or handle as an error


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

# After the chatbot, decide the primary tool path.
workflow.add_conditional_edges(
    "chatbot",
    pre_analysis_router,
    {
        "execute_edit": "execute_edit",
        "should_analyze_vision": "should_analyze_vision",
        "answer_question": "answer_question" # Fallback
    }
)

# For contextual questions, decide whether to run vision analysis.
workflow.add_conditional_edges(
    "should_analyze_vision",
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

# After answering a question, the conversation can continue.
workflow.add_edge("answer_question", "chatbot")
# After an edit is executed, the graph should end for this request-response cycle.
workflow.add_edge("execute_edit", END)

# Compile the graph
app = workflow.compile()
