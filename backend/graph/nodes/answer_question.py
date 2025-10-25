# This node is responsible for answering the user's question.
# It takes the user's question and the video content as input.
# It should generate a helpful answer based on the video content.

from backend.graph.state import GraphState

def answer_question(state: GraphState):
    """
    Placeholder for answering a question.
    """
    print("---ANSWERING QUESTION---")
    print(state["parsed_query"])
    return state
