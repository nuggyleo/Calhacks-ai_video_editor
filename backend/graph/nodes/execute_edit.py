import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional

from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, AIMessage
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

def execute_edit(state: GraphState):
    """
    Main entry point for the video editing agent.
    This node creates a temporary, specialized agent to handle a single edit.
    """
    logger.info("--- VIDEO EDITING AGENT: Starting ---")
    
    # 1. Get context from the main graph state
    media_bin = state.get("media_bin", {})
    active_video_id = state.get("active_video_id")
    parsed_query = state.get("parsed_query", {})
    edit_actions = parsed_query.get("data", [])

    logger.info(f"Active Video ID: {active_video_id}")
    logger.info(f"Media Bin Keys: {list(media_bin.keys())}")
    logger.info(f"Parsed Edit Actions: {edit_actions}")

    if not all([edit_actions, active_video_id, media_bin]):
        logger.error("Missing data for video editing agent. Aborting.")
        return {**state, "error": "Missing data for video editing agent."}

    # 2. Create simplified, "bound" tools for the agent.
    # These tools are dynamically created to capture the current video context.
    # This simplifies the agent's job, as it doesn't need to know about the media_bin.
    @tool
    def trim_video(start_time: float, end_time: Optional[float] = None) -> str:
        """Trims the currently active video."""
        # Call the original tool's underlying function directly
        return video_tools.trim_video.func(
            active_video_id=active_video_id, media_bin=media_bin,
            start_time=start_time, end_time=end_time
        )

    @tool
    def add_text_to_video(text: str, start_time: float, duration: float, position: str = "center", fontsize: int = 70, color: str = 'white') -> str:
        """Adds a text overlay to the currently active video."""
        # Call the original tool's underlying function directly
        return video_tools.add_text_to_video.func(
            active_video_id=active_video_id, media_bin=media_bin,
            text=text, start_time=start_time, duration=duration,
            position=position, fontsize=fontsize, color=color
        )

    @tool
    def apply_filter_to_video(filter_description: str) -> str:
        """Applies a filter to the currently active video."""
        # Call the original tool's underlying function directly
        return video_tools.apply_filter_to_video.func(
            active_video_id=active_video_id, media_bin=media_bin,
            filter_description=filter_description
        )

    @tool
    def change_video_speed(speed_factor: float) -> str:
        """Changes the speed of the currently active video."""
        # Call the original tool's underlying function directly
        return video_tools.change_video_speed.func(
            active_video_id=active_video_id, media_bin=media_bin,
            speed_factor=speed_factor
        )

    @tool
    def concatenate_videos(video_ids: List[str]) -> str:
        """Concatenates the specified videos together."""
        # This tool doesn't need an active_video_id, just the media_bin
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
        """
        Adds or replaces the audio track of a video with an audio file from the media library.
        Use this when the user wants to add background music or replace the audio of a video.
        
        Args:
            video_id: The ID of the video to add audio to (from the media bin).
            audio_id: The ID of the audio file to add (from the media bin).
        """
        return video_tools.add_audio_to_video.func(
            video_id=video_id, audio_id=audio_id, media_bin=media_bin
        )

    tools = [trim_video, add_text_to_video, apply_filter_to_video, change_video_speed, concatenate_videos, extract_audio, add_audio_to_video]

    # 3. Bind tools to the model
    model = ChatOpenAI(temperature=0, streaming=True).bind_tools(tools)
    
    # 4. Check if this is a multi-step task
    is_multi_step = len(edit_actions) > 1
    logger.info(f"Processing {'multi-step' if is_multi_step else 'single-step'} task with {len(edit_actions)} action(s)")
    
    tool_map = {tool.name: tool for tool in tools}
    results = {}  # Store intermediate results (file paths)
    temp_media_ids = {}  # Store temporary media IDs for intermediate files
    final_video_path = None
    
    # Make a mutable copy of media_bin for adding temporary files
    temp_media_bin = dict(media_bin)
    
    # 5. Execute each action in sequence
    for step_idx, action_dict in enumerate(edit_actions):
        logger.info(f"\n--- Executing Step {step_idx + 1}/{len(edit_actions)} ---")
        logger.info(f"Action: {action_dict}")
        
        # Replace placeholders like {{result_of_step_1}} with actual values
        action_str = json.dumps(action_dict)
        for prev_step, prev_result_path in results.items():
            # Check if we need an ID or a path
            placeholder_id = f"{{{{result_of_step_{prev_step}}}}}"
            
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
        
        action_dict = json.loads(action_str)
        
        # Determine which tool to call based on action
        action_name = action_dict.get('action', '')
        
        # Map action names to tool names
        action_to_tool = {
            'trim': 'trim_video',
            'add_text': 'add_text_to_video',
            'filter': 'apply_filter_to_video',
            'speed': 'change_video_speed',
            'concatenate': 'concatenate_videos',
            'extract_audio': 'extract_audio',
            'add_audio_to_video': 'add_audio_to_video'
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
            
            if action_name == 'trim':
                result_path = video_tools.trim_video.func(
                    active_video_id=tool_args.get('video_id', active_video_id),
                    media_bin=temp_media_bin,
                    start_time=tool_args['start_time'],
                    end_time=tool_args.get('end_time')
                )
            elif action_name == 'add_text':
                result_path = video_tools.add_text_to_video.func(
                    active_video_id=tool_args.get('video_id', active_video_id),
                    media_bin=temp_media_bin,
                    text=tool_args['text'],
                    start_time=tool_args['start_time'],
                    duration=tool_args['duration'],
                    position=tool_args.get('position', 'center'),
                    fontsize=tool_args.get('fontsize', 70),
                    color=tool_args.get('color', 'white')
                )
            elif action_name == 'filter':
                result_path = video_tools.apply_filter_to_video.func(
                    active_video_id=tool_args.get('video_id', active_video_id),
                    media_bin=temp_media_bin,
                    filter_description=tool_args['filter_description']
                )
            elif action_name == 'speed':
                result_path = video_tools.change_video_speed.func(
                    active_video_id=tool_args.get('video_id', active_video_id),
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
                    active_video_id=tool_args.get('video_id', active_video_id),
                    media_bin=temp_media_bin
                )
            elif action_name == 'add_audio_to_video':
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
