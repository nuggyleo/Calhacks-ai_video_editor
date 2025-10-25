# This file defines the main langgraph graph.
# It imports the nodes from the 'nodes' directory and connects them to form a graph.
# The graph defines the flow of control and data between the nodes.

from langgraph.graph import StateGraph, END
from backend.graph.state import GraphState
from backend.graph.nodes.query_parser import query_parser
from backend.graph.nodes.answer_question import answer_question
from backend.graph.nodes.execute_edit import execute_edit

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
workflow.add_node("execute_edit", execute_edit)

# Set the entry point
workflow.set_entry_point("query_parser")

# Add the conditional edge from the query parser
workflow.add_conditional_edges(
    "query_parser",
    query_router,
    {
        "answer_question": "answer_question",
        "execute_edit": "execute_edit",
    },
)

# Add edges from the other nodes to the end
workflow.add_edge("answer_question", END)
workflow.add_edge("execute_edit", END)

# Compile the graph
app = workflow.compile()
