import os
from pathlib import Path
from typing import List

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from backend.graph.state import GraphState
from backend.video_engine.editing.effects import apply_filter, add_subtitle, add_caption
from backend.video_engine.editing.audio import set_audio
from backend.video_engine.editing.export import export_video
from backend.ai_services.filter_mapper import map_description_to_filter
from backend.video_engine.tools import trim_video, add_text_to_video, apply_filter_to_video, change_video_speed
from moviepy.editor import VideoFileClip

# 1. Define the tools for the agent
tools = [
    TavilySearchResults(max_results=3),
    trim_video,
    add_text_to_video,
    apply_filter_to_video,
    change_video_speed,
]
tool_node = ToolNode(tools)

# 2. Define the agent model
model = ChatOpenAI(temperature=0, streaming=True).bind_tools(tools)


# 3. Define the nodes for the agent's internal graph
def agent_node(state: GraphState):
    """The agent's "brain" - decides what action to take."""
    print("---AGENT: Deciding next action---")
    response = model.invoke(state["messages"])
    return {"messages": [response]}

def should_continue_router(state: GraphState):
    """Router to decide if the agent should continue or is finished."""
    if state["messages"][-1].tool_calls:
        return "tool_node"
    else:
        return END

# 4. Wire up the agent's internal graph
agent_workflow = StateGraph(GraphState)
agent_workflow.add_node("agent", agent_node)
agent_workflow.add_node("tool_node", tool_node) # Using the official ToolNode
agent_workflow.set_entry_point("agent")
agent_workflow.add_conditional_edges(
    "agent",
    should_continue_router,
)
agent_workflow.add_edge("tool_node", "agent")
agent_app = agent_workflow.compile()


# 5. Define the main entry point for the graph node
def execute_edit(state: GraphState):
    """
    Main entry point for the video editing agent.
    """
    print("---VIDEO EDITING AGENT: Starting---")
    parsed_query = state.get("parsed_query", {})
    edit_actions = parsed_query.get("data", [])

    if not edit_actions:
        return {**state, "error": "No edit actions provided."}

    user_request = f"Perform the following video edits: {str(edit_actions)}"
    video_path = state.get("video_path")
    full_request = f"""User Request: "{user_request}"
    Initial video file path: "{video_path}"

    Your task is to execute a plan to fulfill this request.
    Use the initial video path for your first tool call.
    For any subsequent tool calls, you MUST use the new video path returned by the previous tool.
    
    IMPORTANT: After you have successfully called a tool and received the path to the new video, your job is done.
    Your final answer should be ONLY a short confirmation message, like 'Video editing complete.' Do not output the path.
    """

    initial_agent_state = {
        "messages": [HumanMessage(content=full_request)],
        "video_path": video_path
    }
    
    # Invoke the agent. It will run until it hits the END state.
    final_agent_state = agent_app.invoke(initial_agent_state)
    
    # Extract the final video path from the message history
    final_video_path = video_path # Default to original path
    for message in reversed(final_agent_state["messages"]):
        if isinstance(message, ToolMessage) and ".mp4" in str(message.content):
            final_video_path = str(message.content)
            break

    # Ensure the video is fully written to disk before proceeding
    if final_video_path and os.path.exists(final_video_path):
        # This is a simple way to wait for the file to be ready.
        # For a more robust solution, you might use a file lock or a more sophisticated check.
        pass

    # Construct the public URL for the final video
    output_url = None
    if final_video_path:
        # The URL should be relative to the domain, not the file system.
        output_url = f"/outputs/{Path(final_video_path).name}"

    final_message = f"Video editing complete. Final version available at: {output_url}"

    # Return the final message and output URL to be appended to the history
    return {
        "messages": [AIMessage(
            content=final_message,
            additional_kwargs={"output_url": output_url}
        )]
    }
