# This node is responsible for answering the user's question.
# It takes the user's question and the video content as input.
# It should generate a helpful answer based on the video content.

from backend.graph.state import GraphState
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv
import os
from langchain_core.tools import tool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables from .env file
load_dotenv()

def answer_question(state: GraphState):
    """
    Answers a user's question by giving an agent a tool to fetch video context.
    """
    
    video_description = state.get("video_description", "")
    query = state.get("query", "")

    # 1. Define the tools for the agent
    @tool
    def get_video_content_summary() -> str:
        """
        Returns a detailed summary of the current video's content.
        Call this tool *only* when the user asks a question about the video's content
        or asks for editing suggestions.
        """
        return video_description

    @tool
    def get_project_functionalities() -> str:
        """
        Returns a summary of the video editing features available in this application.
        Call this tool *only* when the user asks what you can do, what features are available, or about your capabilities.
        """
        return """
Here are the main editing features I can help you with:

*   **Trimming:** Shorten your video by specifying start and end times.
*   **Effects & Filters:** Apply a variety of visual effects like black and white, invert colors, and more.
*   **Text Overlays:** Add captions or titles to your video at any timestamp.
*   **Concatenation:** Merge multiple videos together into a single clip.
*   **Speed Control:** Change the playback speed of your video (e.g., slow-motion or fast-forward).
*   **Audio Tools:** Basic audio manipulation is available.
"""

    tools = [get_video_content_summary, get_project_functionalities]

    # 2. Create a focused prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert AI video editing assistant named 'Cue'.
Your primary function is to provide creative and actionable video editing suggestions or information about your own capabilities.

**Your workflow is simple and you must follow it:**
1.  When the user asks for editing ideas or suggestions for their video, you MUST use the `get_video_content_summary` tool.
2.  When the user asks about your capabilities, what you can do, or what features are available, you MUST use the `get_project_functionalities` tool.
3.  The tools are your ONLY way to get this information. **Do not ask the user and do not make up answers.**
4.  After calling a tool, provide a concise, helpful answer based on its output.
5.  If the user asks a general question (e.g., "hello"), you can answer directly without using a tool."""),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    # 3. Create the agent
    api_key = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(temperature=0.7, openai_api_key=api_key)
    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools)

    # 4. Invoke the agent
    response = agent_executor.invoke({"input": query})
    final_answer = response["output"]

    # Append the final answer to the message history
    messages = state.get("messages", [])
    messages.append(AIMessage(content=final_answer))
    
    return {"messages": messages}
