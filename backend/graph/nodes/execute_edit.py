import os
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

    tools = [trim_video, add_text_to_video, apply_filter_to_video, change_video_speed, concatenate_videos]

    # 3. Bind tools to the model
    model = ChatOpenAI(temperature=0, streaming=True).bind_tools(tools)
    
    # 4. Create a simplified prompt and invoke the agent directly
    user_request = f"Perform the following video edits: {str(edit_actions)}"
    full_request = f"""Your task is to execute this user request: "{user_request}"
    
    You must call the appropriate tool to perform the edit. After the tool is called once, your job is complete.
    Your final response should be a simple confirmation message.
    """
    logger.info(f"Agent Prompt:\n{full_request}")
    
    # --- This is the new, simplified logic ---
    response_message = model.invoke([HumanMessage(content=full_request)])
    logger.info(f"Agent Raw Response: {response_message}")

    # 5. Process the response and execute the chosen tool
    final_video_path = None
    if response_message.tool_calls:
        tool_map = {tool.name: tool for tool in tools}
        tool_call = response_message.tool_calls[0] # We only expect one tool call
        tool_name = tool_call['name']
        tool_args = tool_call['args']
        
        logger.info(f"Agent decided to call tool '{tool_name}' with args: {tool_args}")
        
        if tool_name in tool_map:
            selected_tool = tool_map[tool_name]
            # This is where the actual video processing happens
            final_video_path = selected_tool.invoke(tool_args)
        else:
            logger.error(f"Agent tried to call a non-existent tool: {tool_name}")
    else:
        logger.warning("Agent finished without calling a tool.")

    logger.info(f"Extracted final video path: {final_video_path}")
            
    output_url = f"/outputs/{Path(final_video_path).name}" if final_video_path else None
    final_message = f"Video editing complete. Final version available at: {output_url}"
    logger.info(f"Final message for UI: {final_message}")

    return {
        "messages": [AIMessage(
            content=final_message,
            additional_kwargs={"output_url": output_url}
        )]
    }
