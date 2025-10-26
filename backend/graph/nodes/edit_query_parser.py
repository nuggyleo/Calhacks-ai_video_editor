import json
import logging
from pathlib import Path
from typing import List

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI

from backend.graph.state import GraphState

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def edit_query_parser(state: GraphState):
    """
    Parses a user's complex video editing query into a list of simple,
    sequential natural language instructions.
    """
    logger.info("--- EDIT QUERY PARSER: Starting ---")
    
    media_bin = state.get("media_bin", {})
    active_video_id = state.get("active_video_id")
    messages = state.get("messages", [])
    
    if not messages:
        return {**state, "error": "No messages to parse."}

    user_command = messages[-1].content
    
    # Create a simplified context of the media bin for the AI
    media_bin_context = {
        media_id: {
            "filename": Path(path).name,
            "type": "video" if Path(path).suffix.lower() in ['.mp4', '.mov', '.avi', '.webm'] else "audio"
        }
        for media_id, path in media_bin.items()
    }

    PROMPT = f"""You are an expert video editing assistant. Your job is to break down a user's command into a simple, sequential list of natural language instructions for another AI to execute.

**Primary Directive: Determine the Scope**
1.  **Multi-Video Command:** If the user says "each video," "all videos," or "every video," generate an action for EACH video in the media bin.
2.  **Single-Video Command:** Otherwise, all actions apply to the active video.

**Response Format:**
- Your output MUST be a JSON object with a single key "actions" containing a list of strings.
- Each string in the list is one simple, clear instruction for the next AI.
- For sequential actions, you MUST explicitly reference the output of the PREVIOUS step (e.g., "apply a green filter to the result of step 1", "add fade out to the result of step 2"). DO NOT reference older steps in the chain unless absolutely necessary.

**Context:**
- **User Command:** "{user_command}"
- **Active Video ID:** "{active_video_id}"
- **Media Bin:** {json.dumps(media_bin_context, indent=2)}

**Example 1:**
- User Command: "Trim all videos from 4 seconds to 8 seconds."
- (Assuming the Media Bin contains videos with filenames "vid1.mp4" and "vid2.mp4")
- **Your JSON Output:**
  {{
    "actions": [
      "trim video 'vid1.mp4' from 4 seconds to 8 seconds",
      "trim video 'vid2.mp4' from 4 seconds to 8 seconds"
    ]
  }}

**Example 2:**
- User Command: "Trim the video from 00:04 to 00:08 and then apply a green filter."
- **Your JSON Output:**
  {{
    "actions": [
      "trim the active video from 4 seconds to 8 seconds",
      "apply a green filter to the result of step 1"
    ]
  }}
         
**Example 3 (Complex Chain):**
- User Command: "Concatenate video A and video B, then add a fade in, then add a fade out."
- **Your JSON Output:**
 {{
   "actions": [
     "concatenate video A and video B",
     "add a fade in to the result of step 1",
     "add a fade out to the result of step 2"
   ]
 }}

Now, generate the JSON output for the user's command.
"""
    
    model = ChatOpenAI(temperature=0, model="gpt-4-turbo-preview", model_kwargs={"response_format": {"type": "json_object"}})
    
    try:
        response = model.invoke([SystemMessage(content=PROMPT)])
        parsed_response = json.loads(response.content)
        nl_actions = parsed_response.get("actions", [])
        
        if not isinstance(nl_actions, list) or not all(isinstance(i, str) for i in nl_actions):
            raise ValueError("AI did not return a valid list of action strings.")
            
        logger.info(f"Successfully parsed into {len(nl_actions)} natural language actions.")
        return {**state, "parsed_actions": nl_actions}

    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse AI response: {e}")
        return {**state, "error": "Failed to parse the editing command."}
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return {**state, "error": "An unexpected error occurred during parsing."}
