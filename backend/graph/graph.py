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


def combined_router(state: GraphState):
    """
    This single, efficient router determines the next step after the chatbot.
    It checks for direct edits first, then for contextual questions,
    and only routes to vision analysis if absolutely necessary.
    """
    tool_choice = state.get("parsed_query", {}).get("tool_choice")

    if tool_choice == "execute_edit":
        print("--- ROUTING DIRECTLY TO EXECUTE EDIT ---")
        return "execute_edit"
    
    elif tool_choice == "answer_question":
        print("--- ROUTING TO CONTEXTUAL ANALYSIS PATH ---")
        if state.get("video_description"):
            print("--- SKIPPING VISION ANALYSIS (DESCRIPTION ALREADY EXISTS) ---")
            return "query_parser"
        else:
            print("--- ROUTING TO VISION ANALYSIS (NO DESCRIPTION) ---")
            return "vision_analyzer"
    else:
        # Fallback or error handling
        print(f"--- UNKNOWN TOOL CHOICE: {tool_choice}, defaulting to answer_question ---")
        return "answer_question"


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

# After the chatbot, use the combined router to decide the next step.
workflow.add_conditional_edges(
    "chatbot",
    combined_router,
    {
        "execute_edit": "execute_edit",
        "vision_analyzer": "vision_analyzer",
        "query_parser": "query_parser",
        "answer_question": "answer_question" # Fallback
    }
)

# After analyzing, the enriched state goes to the query parser.
workflow.add_edge("vision_analyzer", "query_parser")

# From the query parser, route to the appropriate tool.
# This now only handles the path for answering questions.
workflow.add_conditional_edges(
    "query_parser",
    query_router,
    {
        "answer_question": "answer_question",
        "execute_edit": "execute_edit", # Should not happen, but good to have a path
    },
)

# After answering a question, the conversation can continue.
workflow.add_edge("answer_question", "chatbot")
# After an edit is executed, the graph should end for this request-response cycle.
workflow.add_edge("execute_edit", END)

# Compile the graph
app = workflow.compile()
