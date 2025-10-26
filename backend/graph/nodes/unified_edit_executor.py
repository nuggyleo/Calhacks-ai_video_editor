import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool

from backend.graph.state import GraphState
# Import the original tools so we can wrap them
from backend.video_engine import tools as video_tools

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def unified_edit_executor(state: GraphState):
    """
    Unified node that both parses complex edit queries and executes them.
    This replaces both edit_query_parser and execute_edit nodes.
    """
    logger.info("--- UNIFIED EDIT EXECUTOR: Starting ---")
    
    # Get context from the main graph state
    media_bin = state.get("media_bin", {})
    active_video_id = state.get("active_video_id")
    parsed_query = state.get("parsed_query", {})
    edit_actions = parsed_query.get("data", [])
    messages = state.get("messages", [])

    logger.info(f"Active Video ID: {active_video_id}")
    logger.info(f"Media Bin Keys: {list(media_bin.keys())}")
    logger.info(f"Parsed Edit Actions: {edit_actions}")

    if not all([edit_actions, active_video_id, media_bin]):
        logger.error("Missing data for video editing. Aborting.")
        return {**state, "error": "Missing data for video editing."}

    # Get the user's original command from the last message
    user_command = ""
    if messages:
        last_message = messages[-1]
        if hasattr(last_message, 'content'):
            user_command = last_message.content
        elif isinstance(last_message, dict):
            user_command = last_message.get('content', '')

    logger.info(f"User command: {user_command}")

    # Check if this is a complex command that needs parsing
    # Complex commands are those that don't have proper video_id chaining
    is_complex_command = (
        isinstance(edit_actions, list) and len(edit_actions) > 1 and
        any(action.get('video_id') is None for action in edit_actions if isinstance(action, dict))
    )

    if is_complex_command:
        logger.info("Complex command detected, parsing into atomic actions")
        
        # Create a specialized prompt for parsing complex edit commands
        PARSER_PROMPT = f"""You are an expert video editing command parser. Your job is to break down complex video editing commands into a sequence of simple, atomic actions.

You must analyze the user's command and convert it into a JSON array of individual edit actions. Each action should be simple and executable by a single video editing tool.

Available atomic actions:
1. **trim** - Cut video to specific time range
   Format: {{"action": "trim", "start_time": 0.0, "end_time": 5.0}}
   
2. **add_text** - Add text overlay/captions
   Format: {{"action": "add_text", "text": "caption text", "start_time": 0.0, "duration": 3.0, "position": "center", "fontsize": 70, "color": "white"}}
   
3. **apply_filter** - Apply visual effects/filters
   Format: {{"action": "apply_filter", "filter_description": "description of the filter effect"}}
   
4. **change_speed** - Change video playback speed
   Format: {{"action": "change_speed", "speed_factor": 2.0}}
   
5. **concatenate** - Combine multiple videos
   Format: {{"action": "concatenate", "video_ids": ["id1", "id2"]}}
   
6. **extract_audio** - Extract audio from video
   Format: {{"action": "extract_audio"}}
   
7. **add_audio_to_video** - Add audio track to video
   Format: {{"action": "add_audio_to_video", "video_id": "video_id", "audio_id": "audio_id"}}

Current project state:
- Active Video ID: "{active_video_id}"
- Available Media: {json.dumps(list(media_bin.keys()), indent=2)}

User's command: "{user_command}"

Parse this command into a sequence of atomic actions. Consider:
- Time references (e.g., "from 00:00 to 00:03" = start_time: 0, end_time: 3)
- Text content (extract the exact text to display)
- Filter descriptions (be specific about the visual effect)
- Speed factors (2x = 2.0, 0.5x = 0.5)
- Order of operations (trim first, then add effects)
- Sequential processing: each action should build on the previous result

For sequential edits, use placeholder references:
- First action: use the original video_id
- Subsequent actions: use "{{result_of_step_N}}" where N is the step number

Respond with ONLY a JSON array of actions, no other text.
Example: [{{"action": "trim", "video_id": "original_video_id", "start_time": 0, "end_time": 3}}, {{"action": "apply_filter", "video_id": "{{result_of_step_1}}", "filter_description": "add a blue tint"}}]
"""

        # Initialize the parser model
        model = ChatOpenAI(temperature=0, streaming=True, model_kwargs={"response_format": {"type": "json_object"}})
        
        # Create the message for parsing
        parse_message = [SystemMessage(content=PARSER_PROMPT)]
        
        try:
            # Get the AI's response
            response = model.invoke(parse_message)
            
            # Parse the JSON response
            parsed_actions = json.loads(response.content)
            
            # Ensure it's a list
            if not isinstance(parsed_actions, list):
                parsed_actions = [parsed_actions]
            
            # Process the actions to set up sequential references
            processed_actions = []
            for i, action in enumerate(parsed_actions):
                processed_action = action.copy()
                
                # For the first action, use the active video ID
                if i == 0:
                    processed_action["video_id"] = active_video_id
                else:
                    # For subsequent actions, reference the previous step's result
                    processed_action["video_id"] = f"{{{{result_of_step_{i}}}}}"
                
                processed_actions.append(processed_action)
            
            logger.info(f"Parsed {len(processed_actions)} sequential actions: {processed_actions}")
            edit_actions = processed_actions
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            # Fallback: use the original actions
            pass
        except Exception as e:
            logger.error(f"Error in parsing: {e}")
            # Fallback: use the original actions
            pass

    # Now execute the actions (either original or parsed)
    logger.info(f"Executing {len(edit_actions)} actions")
    
    # Create simplified, "bound" tools for the agent
    @tool
    def trim_video(start_time: float, end_time: Optional[float] = None) -> str:
        """Trims the currently active video."""
        return video_tools.trim_video.func(
            active_video_id=active_video_id, media_bin=media_bin,
            start_time=start_time, end_time=end_time
        )

    @tool
    def add_text_to_video(text: str, start_time: float, duration: float, position: str = "center", fontsize: int = 70, color: str = 'white') -> str:
        """Adds a text overlay to the currently active video."""
        return video_tools.add_text_to_video.func(
            active_video_id=active_video_id, media_bin=media_bin,
            text=text, start_time=start_time, duration=duration,
            position=position, fontsize=fontsize, color=color
        )

    @tool
    def apply_filter_to_video(filter_description: str) -> str:
        """Applies a filter to the currently active video."""
        return video_tools.apply_filter_to_video.func(
            active_video_id=active_video_id, media_bin=media_bin,
            filter_description=filter_description
        )

    @tool
    def change_video_speed(speed_factor: float) -> str:
        """Changes the speed of the currently active video."""
        return video_tools.change_video_speed.func(
            active_video_id=active_video_id, media_bin=media_bin,
            speed_factor=speed_factor
        )

    @tool
    def concatenate_videos(video_ids: List[str]) -> str:
        """Concatenates the specified videos together."""
        return video_tools.concatenate_videos.func(
            video_ids=video_ids, media_bin=media_bin
        )

    @tool
    def extract_audio() -> str:
        """Extracts the audio track from the currently active video and saves it as an MP3 file."""
        return video_tools.extract_audio.func(
            active_video_id=active_video_id, media_bin=media_bin
        )

    @tool
    def add_audio_to_video(video_id: str, audio_id: str) -> str:
        """Adds or replaces the audio track of a video with an audio file from the media library."""
        return video_tools.add_audio_to_video.func(
            video_id=video_id, audio_id=audio_id, media_bin=media_bin
        )

    tools = [trim_video, add_text_to_video, apply_filter_to_video, change_video_speed, concatenate_videos, extract_audio, add_audio_to_video]

    # Check if this is a multi-step task
    is_multi_step = len(edit_actions) > 1
    logger.info(f"Processing {'multi-step' if is_multi_step else 'single-step'} task with {len(edit_actions)} action(s)")
    
    tool_map = {tool.name: tool for tool in tools}
    results = {}  # Store intermediate results (file paths)
    temp_media_ids = {}  # Store temporary media IDs for intermediate files
    final_video_path = None
    
    # Make a mutable copy of media_bin for adding temporary files
    temp_media_bin = dict(media_bin)
    
    # Execute each action in sequence
    for step_idx, action_dict in enumerate(edit_actions):
        logger.info(f"\n--- Executing Step {step_idx + 1}/{len(edit_actions)} ---")
        
        # If a video_id is not specified in the action, default to the active one.
        # This is crucial for the first step of a multi-step edit.
        if 'video_id' not in action_dict:
            action_dict['video_id'] = active_video_id
            
        logger.info(f"Action: {action_dict}")
        
        # Replace placeholders like {{result_of_step_1}} with actual values
        action_str = json.dumps(action_dict)
        logger.info(f"Original action_str: {action_str}")
        logger.info(f"Available results: {results}")
        
        for prev_step, prev_result_path in results.items():
            # Check if we need an ID or a path
            placeholder_id = f"{{{{result_of_step_{prev_step}}}}}"
            logger.info(f"Looking for placeholder: {placeholder_id}")
            
            if placeholder_id in action_str:
                # Get or create a temporary ID for this result
                if prev_step not in temp_media_ids:
                    temp_id = f"temp_result_{prev_step}"
                    temp_media_ids[prev_step] = temp_id
                    temp_media_bin[temp_id] = prev_result_path
                    logger.info(f"Added temporary media: {temp_id} -> {prev_result_path}")
                
                # Replace with the temp ID
                temp_id = temp_media_ids[prev_step]
                logger.info(f"Replacing {placeholder_id} with temp ID: {temp_id}")
                action_str = action_str.replace(f'"{placeholder_id}"', f'"{temp_id}"')
        
        logger.info(f"Final action_str after placeholder replacement: {action_str}")
        
        action_dict = json.loads(action_str)
        
        # Determine which tool to call based on action
        action_name = action_dict.get('action', '')
        
        # Map action names to tool names
        action_to_tool = {
            'trim': 'trim_video',
            'add_text': 'add_text_to_video',
            'add_caption': 'add_text_to_video',  # Support both add_text and add_caption
            'apply_filter': 'apply_filter_to_video',
            'filter': 'apply_filter_to_video',  # Support both for backward compatibility
            'speed': 'change_video_speed',
            'change_speed': 'change_video_speed',  # Support both
            'concatenate': 'concatenate_videos',
            'extract_audio': 'extract_audio',
            'add_audio_to_video': 'add_audio_to_video',
            'add_audio': 'add_audio_to_video'  # Support both
        }
        
        tool_name = action_to_tool.get(action_name, action_name)
        
        if tool_name not in tool_map:
            logger.error(f"Unknown tool: {tool_name}")
            continue
            
        # Prepare arguments (remove 'action' field)
        tool_args = {k: v for k, v in action_dict.items() if k != 'action'}
        
        logger.info(f"Calling tool '{tool_name}' with args: {tool_args}")
        
        try:
            # Call the underlying video_tools functions directly with temp_media_bin
            result_path = None
            
            # IMPORTANT: Use the video_id from the action_dict, not the overall active_video_id
            current_video_id = action_dict.get('video_id', active_video_id)
            
            if action_name == 'trim':
                result_path = video_tools.trim_video.func(
                    active_video_id=current_video_id,
                    media_bin=temp_media_bin,
                    start_time=tool_args['start_time'],
                    end_time=tool_args.get('end_time')
                )
            elif action_name in ['add_text', 'add_caption']:
                result_path = video_tools.add_text_to_video.func(
                    active_video_id=current_video_id,
                    media_bin=temp_media_bin,
                    text=tool_args['text'],
                    start_time=tool_args['start_time'],
                    duration=tool_args['duration'],
                    position=tool_args.get('position', 'center'),
                    fontsize=tool_args.get('fontsize', 70),
                    color=tool_args.get('color', 'white')
                )
            elif action_name in ['filter', 'apply_filter']:
                result_path = video_tools.apply_filter_to_video.func(
                    active_video_id=current_video_id,
                    media_bin=temp_media_bin,
                    filter_description=tool_args['filter_description']
                )
            elif action_name in ['speed', 'change_speed']:
                result_path = video_tools.change_video_speed.func(
                    active_video_id=current_video_id,
                    media_bin=temp_media_bin,
                    speed_factor=tool_args['speed_factor']
                )
            elif action_name == 'concatenate':
                result_path = video_tools.concatenate_videos.func(
                    video_ids=tool_args['video_ids'],
                    media_bin=temp_media_bin
                )
            elif action_name == 'extract_audio':
                result_path = video_tools.extract_audio.func(
                    active_video_id=current_video_id,
                    media_bin=temp_media_bin
                )
            elif action_name in ['add_audio_to_video', 'add_audio']:
                result_path = video_tools.add_audio_to_video.func(
                    video_id=tool_args['video_id'],
                    audio_id=tool_args['audio_id'],
                    media_bin=temp_media_bin
                )
            else:
                logger.error(f"Unknown action: {action_name}")
                continue
            
            logger.info(f"Step {step_idx + 1} completed. Result: {result_path}")
            
            # Store result for potential use in next steps
            results[step_idx + 1] = result_path
            final_video_path = result_path  # The last result is the final output
            
        except Exception as e:
            logger.error(f"Error executing step {step_idx + 1}: {e}")
            raise e

    logger.info(f"Extracted final media path: {final_video_path}")
    
    # Determine if output is audio or video based on file extension
    media_type = "video"
    if final_video_path:
        file_extension = Path(final_video_path).suffix.lower()
        if file_extension in ['.mp3', '.wav', '.m4a', '.aac']:
            media_type = "audio"
            
    output_url = f"/outputs/{Path(final_video_path).name}" if final_video_path else None
    
    if media_type == "audio":
        final_message = f"Audio extraction complete! I've extracted the audio track from your video."
    else:
        final_message = f"Video editing complete! Your edited video is ready."
    
    logger.info(f"Final message for UI: {final_message}")

    return {
        "messages": [AIMessage(
            content=final_message,
            additional_kwargs={
                "output_url": output_url,
                "media_type": media_type,
                "filename": Path(final_video_path).name if final_video_path else None
            }
        )]
    }
