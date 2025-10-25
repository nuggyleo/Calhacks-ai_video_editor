# This node is responsible for answering the user's question.
# It takes the user's question and the video content as input.
# It should generate a helpful answer based on the video content.

from backend.graph.state import GraphState
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def answer_question(state: GraphState):
    """
    Answers a question based on the parsed query.
    """
    print("---ANSWERING QUESTION---")
    parsed_query = state.get("parsed_query", {})
    question = parsed_query.get("data", {}).get("question", "Could not find question.")

    # Updated model invocation
    model = ChatOpenAI(model="gpt-4o", temperature=0, api_key=os.environ.get("OPENAI_API_KEY"))
    response = model.invoke(f"You are a helpful video assistant. A user asked the following question: '{question}'. Provide a concise and helpful response based on the video's content.")
    
    return {
        **state,
        "result": {
            "status": "completed",
            "message": response.content
        }
    }
