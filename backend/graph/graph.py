# This file defines the main langgraph graph.
# It imports the nodes from the 'nodes' directory and connects them to form a graph.
# The graph defines the flow of control and data between the nodes.

from langgraph.graph import StateGraph, END

from backend.graph.state import GraphState
from backend.graph.nodes.answer_question import answer_question
from backend.graph.nodes.execute_edit import execute_edit
from backend.graph.nodes.chatbot import chatbot
from backend.graph.nodes.vision_analyzer import vision_analyzer_node


def master_router(state: GraphState):
    """
    This master router implements the user's two-step validation logic.
    It intelligently decides the most efficient path for the query.
    """
    tool_choice = state.get("parsed_query", {}).get("tool_choice")
    print(f"--- MASTER ROUTER: Tool choice is '{tool_choice}' ---")

    if tool_choice == "execute_edit":
        print("--- Routing to: execute_edit ---")
        return "execute_edit"
    
    if tool_choice == "functional_question":
        # Step 1 Check PASSED (Intent is functional). Skip all vision checks.
        print("--- Routing to: answer_question (functional) ---")
        return "answer_question"
    
    if tool_choice == "contextual_question":
        # Step 1 Check PASSED (Intent is contextual). Proceed to Step 2.
        if state.get("video_description"):
            # Step 2 Check PASSED (Context exists).
            print("--- Routing to: answer_question (context exists) ---")
            return "answer_question"
        else:
            # Step 2 Check FAILED (Context needed).
            print("--- Routing to: vision_analyzer (context needed) ---")
            return "vision_analyzer"
    
    # Fallback in case of an unknown tool choice
    print(f"--- WARNING: Unknown tool choice '{tool_choice}'. Defaulting to answer_question path. ---")
    return "answer_question"

workflow = StateGraph(GraphState)

# Add the nodes
workflow.add_node("chatbot", chatbot)
workflow.add_node("answer_question", answer_question)
workflow.add_node("execute_edit", execute_edit)
workflow.add_node("vision_analyzer", vision_analyzer_node)

# Set the entry point
workflow.set_entry_point("chatbot")

# Main routing logic from the chatbot
workflow.add_conditional_edges(
    "chatbot",
    master_router,
    {
        "execute_edit": "execute_edit",
        "vision_analyzer": "vision_analyzer",
        "answer_question": "answer_question",
    }
)

# After vision analysis, the flow must proceed to answer the question.
workflow.add_edge("vision_analyzer", "answer_question")

# Both paths must end to return a response to the web request.
workflow.add_edge("answer_question", END) # End after answering
workflow.add_edge("execute_edit", END)    # End after an edit

# Compile the graph
app = workflow.compile()
