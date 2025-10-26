import json
import logging
from pathlib import Path
from typing import List, Dict, Optional

from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolExecutor, ToolInvocation

from backend.graph.state import GraphState
from backend.video_engine import tools as video_tools

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def unified_edit_executor(state: GraphState):
    """
    Executes a list of natural language editing instructions by dynamically
    parsing each step into a tool call and dispatching it.
    """
    logger.info("--- UNIFIED EDIT EXECUTOR (Action Executor): Starting ---")
    
    media_bin = state.get("media_bin", {})
    nl_actions = state.get("parsed_actions", [])
    active_video_id = state.get("active_video_id")

    if not nl_actions:
        return {**state, "error": "No actions to execute."}

    # --- Agentic Tool Definitions ---
    # These wrappers provide the necessary context (media_bin) to the core tool functions.
    @tool
    def trim_video(video_id: str, start_time: float, end_time: float) -> str:
        """Trims a video to a specific start and end time."""
        return video_tools.trim_video(video_id=video_id, media_bin=temp_media_bin, start_time=start_time, end_time=end_time)

    @tool
    def add_text_to_video(video_id: str, text: str, start_time: float, duration: float, position: str = "center", fontsize: int = 70, color: str = 'white') -> str:
        """Adds a text overlay to a video."""
        return video_tools.add_text_to_video(video_id=video_id, media_bin=temp_media_bin, text=text, start_time=start_time, duration=duration, position=position, fontsize=fontsize, color=color)

    @tool
    def apply_filter_to_video(video_id: str, filter_description: str) -> str:
        """Applies a visual filter or transition to a video."""
        return video_tools.apply_filter_to_video(video_id=video_id, media_bin=temp_media_bin, filter_description=filter_description)

    @tool
    def change_video_speed(video_id: str, speed_factor: float) -> str:
        """Changes the playback speed of a video."""
        return video_tools.change_video_speed(video_id=video_id, media_bin=temp_media_bin, speed_factor=speed_factor)

    @tool
    def concatenate_videos(video_ids: List[str]) -> str:
        """Combines multiple videos into a single video."""
        return video_tools.concatenate_videos(video_ids=video_ids, media_bin=temp_media_bin)

    @tool
    def extract_audio(video_id: str) -> str:
        """Extracts the audio track from a video."""
        return video_tools.extract_audio(video_id=video_id, media_bin=temp_media_bin)

    @tool
    def add_audio_to_video(video_id: str, audio_id: str) -> str:
        """Adds an audio track to a video."""
        return video_tools.add_audio_to_video(video_id=video_id, audio_id=audio_id, media_bin=temp_media_bin)
    
    @tool
    def extract_and_add_audio(source_video_id: str, destination_video_id: str) -> str:
        """Extracts audio from one video and adds it to another."""
        return video_tools.extract_and_add_audio(source_video_id=source_video_id, destination_video_id=destination_video_id, media_bin=temp_media_bin)

    tools = [trim_video, add_text_to_video, apply_filter_to_video, change_video_speed, concatenate_videos, extract_audio, add_audio_to_video, extract_and_add_audio]
    tool_executor = ToolExecutor(tools)
    
    results = {}
    temp_media_bin = dict(media_bin)
    temp_media_ids = {}
    final_outputs = []

    TOOL_CALLER_PROMPT_TEMPLATE = """You are a precise AI tool-calling assistant. Your ONLY job is to convert a natural language instruction into a single, valid JSON tool call based on the available tools.

**Available Tools & Formats:**
- `trim_video(video_id: str, start_time: float, end_time: float)`
- `add_text_to_video(video_id: str, text: str, start_time: float, duration: float, position: str = "center", ...)`
- `apply_filter_to_video(video_id: str, filter_description: str)` - Use for filters and transitions like "fade_in", "fade_out".
- `change_video_speed(video_id: str, speed_factor: float)`
- `concatenate_videos(video_ids: List[str])`
- `extract_audio(video_id: str)`
- `add_audio_to_video(video_id: str, audio_id: str)`
- `extract_and_add_audio(source_video_id: str, destination_video_id: str)`

**CRITICAL RULES:**
1.  **Output ONLY the JSON tool call.** Your entire response should be a single JSON object.
2.  The "action" field in your JSON MUST match one of the available tool names exactly.
3.  If the instruction refers to a result from a previous step (e.g., "the edited video"), you MUST use the placeholder `{{{{result_of_step_N}}}}` for the `video_id` or `audio_id`.
4.  If the instruction mentions a filename (e.g., "video1.mp4"), use that to find the corresponding ID from the Media Bin context. 
5.  If no specific video is mentioned and it's the first step, assume the target is the `active_video_id`.

**Context:**
- **Instruction to parse:** "{instruction}"
- **Active Video ID:** "{active_video_id}"
- **Media Bin (filename: id):** {media_bin_context}
- **Results of previous steps (for placeholders):** {results_context}

Now, generate the single JSON tool call for the instruction.
"""

    model = ChatOpenAI(temperature=0, model="gpt-4-turbo-preview", model_kwargs={"response_format": {"type": "json_object"}})
    
    media_bin_context = {Path(p).name: i for i, p in media_bin.items()}

    for step_idx, instruction in enumerate(nl_actions):
        logger.info(f"--- Executor: Step {step_idx + 1}/{len(nl_actions)} ---")
        logger.info(f"Instruction: '{instruction}'")

        try:
            prompt = TOOL_CALLER_PROMPT_TEMPLATE.format(
                instruction=instruction,
                results_context=json.dumps(list(results.keys())),
                active_video_id=active_video_id,
                media_bin_context=json.dumps(media_bin_context)
            )
            response = model.invoke([SystemMessage(content=prompt)])
            
            action_dict = json.loads(response.content)
            
            # Handle potential nesting of the tool call
            if "tool_call" in action_dict:
                 action_dict = action_dict["tool_call"]
            elif "action" not in action_dict and len(action_dict) == 1:
                tool_name = next(iter(action_dict.keys()))
                tool_args = action_dict[tool_name]
                action_dict = {"action": tool_name, **tool_args}

            tool_name = action_dict.pop('action')
            tool_args = action_dict

            # Substitute placeholders in the arguments with temporary IDs
            args_str = json.dumps(tool_args)
            for prev_step, prev_result_path in results.items():
                placeholder = f"{{{{result_of_step_{prev_step}}}}}"
                if placeholder in args_str:
                    if prev_step not in temp_media_ids:
                        temp_id = f"temp_result_{prev_step}"
                        temp_media_ids[prev_step] = temp_id
                        temp_media_bin[temp_id] = prev_result_path
                    
                    temp_id_to_use = temp_media_ids[prev_step]
                    args_str = args_str.replace(f'"{placeholder}"', f'"{temp_id_to_use}"')
            
            tool_args = json.loads(args_str)

            logger.info(f"Dispatching tool call: {tool_name}({tool_args})")

            invocation = ToolInvocation(tool=tool_name, tool_input=tool_args)
            tool_result_message = tool_executor.batch([invocation])[0]
            
            result_path = tool_result_message.content
            logger.info(f"Step {step_idx + 1} completed. Result: {result_path}")
            
            results[step_idx + 1] = result_path
            
            is_dependency = any(f"step {step_idx + 1}" in act for act in nl_actions[step_idx+1:])
            if not is_dependency:
                final_outputs.append(result_path)

        except Exception as e:
            logger.error(f"Error executing action for instruction '{instruction}': {e}", exc_info=True)
            return {**state, "error": f"Error during editing: {e}"}

    if not final_outputs:
        if results:
            final_outputs.append(results[max(results.keys())])
        else:
            return {**state, "messages": [AIMessage(content="No final output was generated.")]}

    if len(final_outputs) > 1:
        final_message = f"Successfully created {len(final_outputs)} new videos. They have been added to your media bin."
        return {**state, "messages": [AIMessage(content=final_message)]}
    
    final_media_path = final_outputs[0]
    output_url = f"/outputs/{Path(final_media_path).name}" if final_media_path else None
    
    final_message = "Video editing complete! Your new video is ready."
    
    return {
        **state,
        "messages": [AIMessage(content=final_message, additional_kwargs={"output_url": output_url, "filename": Path(final_media_path).name if final_media_path else None})]
    }
