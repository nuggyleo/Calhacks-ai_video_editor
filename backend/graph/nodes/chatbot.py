<<<<<<< HEAD
=======
from typing import List
import json
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from pathlib import Path

from backend.graph.state import GraphState

# This is the new, powerful prompt for our chatbot.
# It instructs the AI on its role, capabilities, and the JSON output format.
SYSTEM_PROMPT = """You are an expert AI video editing assistant. You are working in a multi-video environment.
Your first task is to analyze the user's query and the current project state to determine the most efficient action. The project state includes a `media_bin` (a dictionary of available videos) and an `active_video_id` (the video the user is currently focused on).

You must classify the query into one of the following categories and format your response as a JSON object with a "tool_choice" and a "data" payload.

**1. Direct Edit (`tool_choice`: "execute_edit")**
If the user provides a direct command for the `active_video_id`.
*   **Context:** The user might say "this video," which always refers to the `active_video_id`.
*   **Ambiguity:** If the user's command is ambiguous (e.g., "trim the clip to 5s" when there are multiple clips), you must ask for clarification by choosing the "functional_question" tool.
*   **JSON Format:** `{"tool_choice": "execute_edit", "data": [{"action": "action_name", ...}]}`
*   **Example:** "Trim this video from 10s to 30s." -> `{"action": "trim", "start_time": 10, "end_time": 30}`

**2. Functional Question (`tool_choice`: "functional_question")**
If the user asks a general question about your capabilities or if their command is ambiguous and you need to ask for clarification.
*   **JSON Format:** `{"tool_choice": "functional_question", "data": {"question": "Your clarifying question or the user's original query"}}`
*   **Example (Ambiguity):** User says "delete the video." You ask, "Which video would you like me to delete?"

**3. Contextual Question (`tool_choice`: "contextual_question")**
If the user asks a question about the content of the `active_video_id`.
*   **JSON Format:** `{"tool_choice": "contextual_question", "data": {"question": "The user's original query"}}`

You MUST respond with a single JSON object. Your primary job is to be an efficient router.
"""

def chatbot(state: GraphState):
    """
    Acts as the brain of the graph. It uses the full conversation history
    and project context to parse the user's latest query into a structured JSON format.
    """
    
    # Get the project context from the state
    media_bin = state.get("media_bin", {})
    active_video_id = state.get("active_video_id")

    # Format the context for the prompt
    # We only need filename and a generic identifier like "Video 1", "Video 2" for the AI
    media_bin_context = {
        vid_id: {"filename": Path(path).name}
        for vid_id, path in media_bin.items()
    }

    # This is the new, powerful prompt for our chatbot.
    SYSTEM_PROMPT = f"""You are an expert AI video editing assistant. You are working in a multi-video environment.
Your first task is to analyze the user's query and the current project state to determine the most efficient action. The project state includes a `media_bin` (a dictionary of available videos) and an `active_video_id` (the video the user is currently focused on).

You must classify the query into one of the following categories and format your response as a JSON object with a "tool_choice" and a "data" payload.

**1. Direct Edit (`tool_choice`: "execute_edit")**
If the user provides a direct command for the `active_video_id`.
*   **Context:** The user might say "this video," which always refers to the `active_video_id`.
*   **Ambiguity:** If the user's command is ambiguous (e.g., "trim the clip to 5s" when there are multiple clips), you must ask for clarification by choosing the "functional_question" tool.
*   **JSON Format:** `{{"tool_choice": "execute_edit", "data": [{{"action": "action_name", ...}}]}}`
*   **Example:** "Trim this video from 10s to 30s." -> `{{"action": "trim", "start_time": 10, "end_time": 30}}`

**2. Functional Question (`tool_choice`: "functional_question")**
If the user asks a general question about your capabilities or if their command is ambiguous and you need to ask for clarification.
*   **JSON Format:** `{{"tool_choice": "functional_question", "data": {{"question": "Your clarifying question or the user's original query"}}}}`
*   **Example (Ambiguity):** User says "delete the video." You ask, "Which video would you like me to delete?"

**3. Contextual Question (`tool_choice`: "contextual_question")**
If the user asks a question about the content of the `active_video_id`.
*   **JSON Format:** `{{"tool_choice": "contextual_question", "data": {{"question": "The user's original query"}}}}`

You MUST respond with a single JSON object. Your primary job is to be an efficient router.

You are working in a multi-video environment. Here is the current state of the project's media bin:
{json.dumps(media_bin_context, indent=2)}

The currently active video ID is "{active_video_id}". "This video" or "the current video" refers to the active video.

**4. Concatenate Videos (`tool_choice`: "execute_edit")**
If the user wants to combine, merge, or concatenate videos. You must resolve their descriptions (e.g., "the first video", "the one named 'beach.mp4'") into a list of exact video IDs from the media bin context provided above.
*   **JSON Format:** `{{"tool_choice": "execute_edit", "data": [{{"action": "concatenate", "video_ids": ["id_1", "id_2", ...]}}]}}`
*   **Example:** User says "combine the first two videos." You look at the media bin, find the IDs for the first two entries, and generate the action.
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
>>>>>>> 763f6fb39346b173251c0b36b8f4658d302cfd97
