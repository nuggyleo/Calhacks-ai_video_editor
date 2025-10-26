import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
import re

from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

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

    # Use the tools directly from the video_engine
    tools = [
        video_tools.trim_video,
        video_tools.add_text_to_video,
        video_tools.apply_filter_to_video,
        video_tools.change_video_speed,
        video_tools.concatenate_videos,
        video_tools.extract_audio,
        video_tools.add_audio_to_video,
        video_tools.extract_and_add_audio
    ]
    tool_map = {t.name: t for t in tools}
    
    results = {}
    temp_media_bin = dict(media_bin)
    temp_media_ids = {}
    final_outputs = []

    TOOL_CALLER_PROMPT_TEMPLATE = """You are a precise AI tool-calling assistant. Your ONLY job is to convert a natural language instruction into a single, valid JSON tool call based on the available tools.

**Available Tools & Formats:**
- `trim_video(active_video_id: str, start_time: float, end_time: float)`
- `add_text_to_video(active_video_id: str, text: str, start_time: float, duration: float, position: str = "center", ...)`
- `apply_filter_to_video(active_video_id: str, filter_description: str)`
- `change_video_speed(active_video_id: str, speed_factor: float)`
- `concatenate_videos(video_ids: List[str])`
- `extract_audio(active_video_id: str)`
- `add_audio_to_video(video_id: str, audio_id: str)`
- `extract_and_add_audio(source_video_id: str, destination_video_id: str)`

**CRITICAL RULES:**
1.  **Output ONLY the JSON tool call.** Your entire response should be a single JSON object.
2.  The "action" field in your JSON MUST match one of the available tool names exactly.
3.  If the instruction refers to a result from a previous step (e.g., "the edited video"), you MUST use the placeholder `{{{{result_of_step_N}}}}` for the ID.
4.  If the instruction mentions a filename (e.g., "video1.mp4"), find its ID from the Media Bin context and use the ID.
5.  If no specific video is mentioned and it's the first step, use the `active_video_id` for the `active_video_id` parameter.

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
            
            if "action" not in action_dict and len(action_dict) == 1:
                tool_name = next(iter(action_dict.keys()))
                tool_args = action_dict[tool_name]
                action_dict = {"action": tool_name, **tool_args}

            tool_name = action_dict.pop('action')
            tool_args = action_dict

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

            # Add the media_bin to the arguments for the direct tool call
            tool_args['media_bin'] = temp_media_bin

            logger.info(f"Dispatching tool call: {tool_name}({tool_args})")

            if tool_name in tool_map:
                tool_function = tool_map[tool_name]
                # This function invokes the tool and handles the result.
                result_from_tool = tool_function.invoke(tool_args)

                # --- Robust Result Handling ---
                result_path = None
                if tool_function.name == "extract_audio":
                    try:
                        audio_info = json.loads(result_from_tool)
                        result_path = audio_info["output_path"]
                        new_audio_id = audio_info["audio_id"]
                        temp_media_bin[new_audio_id] = result_path # Manually update the media bin
                        logger.info(f"Handled extract_audio output. Path: {result_path}, New ID: {new_audio_id}")
                    except (json.JSONDecodeError, KeyError):
                        logger.error(f"Could not parse result from extract_audio: {result_from_tool}")
                        result_path = result_from_tool # Fallback
                else:
                    # For all other tools, the result is assumed to be a direct file path
                    result_path = result_from_tool


                # Store result for future steps
                temp_id = f"temp_result_{step_idx}"
                results[step_idx + 1] = result_path # Always store the path
                temp_media_bin[temp_id] = result_path # Always map the temp ID to the path

                logger.info(f"Step {step_idx + 1} completed. Result: {result_path}")
                
                is_dependency = any(f"step {step_idx + 1}" in act for act in nl_actions[step_idx+1:])
                if not is_dependency:
                    final_outputs.append(result_path)

            else:
                raise ValueError(f"Unknown tool: {tool_name}")

        except Exception as e:
            logger.error(f"An error occurred during tool execution: {e}")
            # Optionally, you can add the error to the state to be surfaced to the user
            return {**state, "error": f"Error during editing: {e}"}

    # --- Definitive Final Output Logic v2 ---
    final_outputs = []
    user_query = state.get("query", "").lower()
    
    # Check for explicit user intent for a single video output.
    # Also, any concatenation implies a single final video.
    wants_single_video = "single video" in user_query or \
                         "a video" in user_query or \
                         "one video" in user_query or \
                         any("concatenate" in action.lower() for action in nl_actions)

    if wants_single_video:
        # If the user's intent is a single video, the final output is ALWAYS the result of the last step.
        if results:
            last_step = max(results.keys())
            final_outputs.append(results[last_step])
    else:
        # Otherwise, for parallel/batch operations, use the dependency graph to find all
        # outputs that are not used as inputs by subsequent steps.
        if results:
            input_steps = set()
            for instruction in nl_actions:
                matches = re.findall(r"result of step (\d+)", instruction)
                for match in matches:
                    input_steps.add(int(match))

            for step_num, result_path in results.items():
                if step_num not in input_steps:
                    final_outputs.append(result_path)
            
            # Failsafe: if for some reason the above yields nothing, take the last result.
            if not final_outputs and results:
                last_step = max(results.keys())
                final_outputs.append(results[last_step])

    if not final_outputs and results:
        final_outputs.append(results[max(results.keys())])
    elif not final_outputs:
        # Handle case where no edits were made or failed
        return {**state, "messages": [AIMessage(content="No final output was generated.")]}

    # --- FINAL RESPONSE ---
    # The `output_files` field will now be populated for the frontend to render.
    final_output_urls = [f"/outputs/{Path(p).name}" for p in final_outputs]

    if len(final_outputs) > 1:
        final_message = f"Successfully created {len(final_outputs)} new videos. They have been added to your media bin."
        return {
            **state,
            "output_files": final_outputs,
            "messages": [AIMessage(
                content=final_message,
                additional_kwargs={"output_urls": final_output_urls}
            )]
        }
    
    # Single output case remains the same
    final_media_path = final_outputs[0]
    output_url = f"/outputs/{Path(final_media_path).name}" if final_media_path else None
    
    final_message = "Video editing complete! Your new video is ready."
    
    return {
        **state,
        "output_files": final_outputs,
        "messages": [AIMessage(
            content=final_message,
            additional_kwargs={"output_url": output_url, "filename": Path(final_media_path).name if final_media_path else None}
        )]
    }
