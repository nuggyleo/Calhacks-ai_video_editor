from typing import List
import json
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from pathlib import Path

from backend.graph.state import GraphState

def chatbot(state: GraphState):
    """
    Acts as the brain of the graph. It uses the full conversation history
    and project context to parse the user's latest query into a structured JSON format.
    """
    
    # Get the project context from the state
    media_bin = state.get("media_bin", {})
    media_file_info = state.get("media_file_info", {})
    active_video_id = state.get("active_video_id")

    print(f"[CHATBOT] Received media_file_info: {media_file_info}")

    # Format the context for the prompt
    # Use frontend-provided file info if available, otherwise infer from path
    media_bin_context = {}
    for vid_id, path in media_bin.items():
        if vid_id in media_file_info:
            # Use frontend-provided info (includes user-set filenames)
            media_bin_context[vid_id] = media_file_info[vid_id]
        else:
            # Fallback: detect from file path
            filename = Path(path).name
            ext = Path(path).suffix.lower()
            media_type = "audio" if ext in ['.mp3', '.wav', '.m4a', '.aac'] else "video"
            media_bin_context[vid_id] = {"filename": filename, "type": media_type}
    
    print(f"[CHATBOT] Final media_bin_context: {json.dumps(media_bin_context, indent=2)}")

    # This is the new, powerful prompt for our chatbot.
    SYSTEM_PROMPT = f"""You are an expert AI video editing assistant. You are working in a multi-media environment with both videos and audio files.
Your first task is to analyze the user's query and the current project state to determine the most efficient action. The project state includes a `media_bin` (a dictionary of available videos and audio files) and an `active_video_id` (the video the user is currently focused on).

You must classify the query into one of three tool choices: "execute_edit", "functional_question", or "contextual_question".

1.  **`tool_choice`: "execute_edit"**
    - Use this for any direct command to modify the video (e.g., "trim the video", "add a red filter", "cut the corners").
    - The `data` field must be a **FLAT** list of action objects. **DO NOT nest actions inside other actions.**
    - **IMPORTANT**: For sequential edits (multiple actions), use proper video_id chaining:
      - First action: use the active_video_id or specific video_id
      - Subsequent actions that depend on previous results: use "{{{{result_of_step_N}}}}" where N is the 1-based step number
    - **IMPORTANT**: For fade in/out effects, use exact filter names:
      - "fade in" should use `"filter_description": "fadein"`
      - "fade out" should use `"filter_description": "fadeout"`
    - Example 1: "blur the video" -> `{{"tool_choice": "execute_edit", "data": [{{"action": "apply_filter", "filter_description": "blur the video"}}]}}`
    - Example 2: "cut from 5 to 10 seconds" -> `{{"tool_choice": "execute_edit", "data": [{{"action": "trim", "start_time": 5, "end_time": 10}}]}}`
    - Example 3: "crop the edges" -> `{{"tool_choice": "execute_edit", "data": [{{"action": "apply_filter", "filter_description": "crop the edges"}}]}}`
    - Example 4: "add captions saying 'hello world'" -> `{{"tool_choice": "execute_edit", "data": [{{"action": "add_text", "video_id": "{active_video_id}", "text": "hello world", "start_time": 0, "duration": 5}}]}}`
    - Example 5: "speed up the video by 2x" -> `{{"tool_choice": "execute_edit", "data": [{{"action": "change_speed", "video_id": "{active_video_id}", "speed_factor": 2.0}}]}}`
    - Example 6: "trim from 00:00 to 00:03 and then add a filter" -> `{{"tool_choice": "execute_edit", "data": [{{"action": "trim", "video_id": "{active_video_id}", "start_time": 0, "end_time": 3}}, {{"action": "apply_filter", "video_id": "{{{{result_of_step_1}}}}", "filter_description": "add a filter"}}]}}`
    - Example 7: "add a green filter, then trim till 00:03" -> `{{"tool_choice": "execute_edit", "data": [{{"action": "apply_filter", "video_id": "{active_video_id}", "filter_description": "add a green filter"}}, {{"action": "trim", "video_id": "{{{{result_of_step_1}}}}", "start_time": 0, "end_time": 3}}]}}`
    - Example 8: "extract audio from 'video1.mp4' and add it to 'video2.mp4'" -> `{{"tool_choice": "execute_edit", "data": [{{"action": "extract_and_add_audio", "source_video_id": "id_for_video1.mp4", "destination_video_id": "id_for_video2.mp4"}}]}}`
    - Example 9: "trim each video from 10 to 14 seconds, concatenate them, then add fade in and fade out" -> `{{"tool_choice": "execute_edit", "data": [{{"action": "trim", "video_id": "video1_id", "start_time": 10, "end_time": 14}}, {{"action": "trim", "video_id": "video2_id", "start_time": 10, "end_time": 14}}, {{"action": "concatenate", "video_ids": ["{{{{result_of_step_1}}}}", "{{{{result_of_step_2}}}}"]"}}, {{"action": "apply_filter", "video_id": "{{{{result_of_step_3}}}}", "filter_description": "fadein"}}, {{"action": "apply_filter", "video_id": "{{{{result_of_step_4}}}}", "filter_description": "fadeout"}}]}}`

2.  **`tool_choice`: "functional_question"**
    - Use this for questions about your capabilities, features, or how to use the system (NOT about video content).
    - Example: "what filters do you have?" -> `{{"tool_choice": "functional_question", "data": {{"question": "what filters do you have?"}}}}`
    - Example: "what can you do?" -> `{{"tool_choice": "functional_question", "data": {{"question": "what can you do?"}}}}`

3.  **`tool_choice`: "contextual_question"**
    - Use this for questions about the VIDEO'S CONTENT (what's in the video, what happens in the video, etc.).
    - This will trigger vision analysis if needed.
    - Example: "what is this video about?" -> `{{"tool_choice": "contextual_question", "data": {{"question": "what is this video about?"}}}}`
    - Example: "what's happening in the video?" -> `{{"tool_choice": "contextual_question", "data": {{"question": "what's happening in the video?"}}}}`
    - Example: "describe the content" -> `{{"tool_choice": "contextual_question", "data": {{"question": "describe the content"}}}}`

Current project state:
- Media Bin: {json.dumps(media_bin_context, indent=2)}
- Active Video ID: "{active_video_id}"

Your entire response must be only the JSON object.
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
