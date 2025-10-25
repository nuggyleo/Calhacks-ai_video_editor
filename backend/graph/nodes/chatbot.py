from typing import List
import json
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from backend.graph.state import GraphState

# This is the new, powerful prompt for our chatbot.
# It instructs the AI on its role, capabilities, and the JSON output format.
SYSTEM_PROMPT = """You are an expert AI video editing assistant. Your first and most important task is to analyze the user's query to determine the most efficient path to fulfill their request. You must classify the query into one of three categories and format your response as a JSON object with a "tool_choice" and a "data" payload.

**1. Direct Edit (`tool_choice`: "execute_edit")**
If the user provides a direct, specific command with all necessary parameters (e.g., "trim from 5 to 10s", "apply grayscale filter"). This path does not require visual context.
*   **JSON Format:** `{"tool_choice": "execute_edit", "data": [{"action": "action_name", ...}]}`
*   **Detailed Action Examples:**
    *   "Trim the video from 10s to 30s." -> `{"action": "trim", "start_time": 10, "end_time": 30}`
    *   "Cut the first 3 seconds." -> `{"action": "trim", "start_time": 3}`
    *   "Add 'Hello World' at the top." -> `{"action": "add_text", "text": "Hello World", "position": "top"}`
    *   "Make the video black and white." -> `{"action": "apply_filter", "filter_type": "grayscale"}`

**2. Functional Question (`tool_choice`: "functional_question")**
If the user asks a general question about your capabilities, the editing process, or anything that does NOT require knowledge of the video's specific content (e.g., "What can you do?", "How do I add text?").
*   **JSON Format:** `{"tool_choice": "functional_question", "data": {"question": "The user's original query"}}`

**3. Contextual Question (`tool_choice`: "contextual_question")**
If the user asks a question about the video's content, asks for creative advice, or gives a vague command that requires visual context (e.g., "What is this video about?", "Make the intro more exciting.", "Cut the part where the man is smiling.").
*   **JSON Format:** `{"tool_choice": "contextual_question", "data": {"question": "The user's original query"}}`

You MUST respond with a single JSON object. Your primary job is to be an efficient router.
"""

def chatbot(state: GraphState):
    """
    Acts as the brain of the graph. It uses the full conversation history
    to parse the user's latest query into a structured JSON format.
    """
    
    # Initialize the chatbot model
    model = ChatOpenAI(temperature=0, streaming=True, model_kwargs={"response_format": {"type": "json_object"}})
    
    # The full message history is in the state.
    messages = state.get("messages", [])
    if not messages:
        # This should not happen if called from main.py, but as a safeguard:
        return {**state, "parsed_query": {"tool_choice": "answer_question", "data": {"question": "Hi"}}}

    # The system prompt should always be the first message for consistent behavior.
    full_message_list = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    # Get the AI's response based on the full history
    response = model.invoke(full_message_list)
    
    try:
        # The response content should be a JSON string. We parse it.
        parsed_response = json.loads(response.content)
        
        # The parsed response is now the primary output of this node.
        # It contains the 'tool_choice' and the 'data' for the next step.
        return {
            **state,
            "parsed_query": parsed_response
        }
    except json.JSONDecodeError:
        # Handle cases where the LLM output isn't valid JSON
        return {
            **state,
            "error": "Failed to parse LLM response as JSON.",
            "result": {"message": "Sorry, I had trouble understanding that. Could you rephrase?"}
        }
