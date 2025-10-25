from typing import List
import json
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from backend.graph.state import GraphState

# This is the new, powerful prompt for our chatbot.
# It instructs the AI on its role, capabilities, and the JSON output format.
SYSTEM_PROMPT = """You are an expert AI video editing assistant. Your first and most important task is to analyze the user's query to determine the most efficient path to fulfill their request. You must classify the query into one of two categories and format your response as a JSON object with a "tool_choice" and a "data" payload.

**1. Direct Edit (`tool_choice`: "execute_edit")**
If the user provides a direct, specific, and unambiguous command that contains all the necessary parameters for an edit, you must choose this path. This is for commands that DO NOT require you to see or understand the video's content.

*   **JSON Format for `direct_edit`:**
    ```json
    {
      "tool_choice": "execute_edit",
      "data": [
        {
          "action": "action_name",
          ...action_parameters
        }
      ]
    }
    ```

*   **Detailed Action Examples:**
    *   **User:** "Trim the video from 10 seconds to 30 seconds."
        `{"action": "trim", "start_time": 10, "end_time": 30}`
    *   **User:** "Cut the first 3 seconds."
        `{"action": "trim", "start_time": 3}`
    *   **User:** "Add the text 'Hello World' at the top of the screen."
        `{"action": "add_text", "text": "Hello World", "position": "top"}`
    *   **User:** "Make the video black and white."
        `{"action": "apply_filter", "filter_type": "grayscale"}`

**2. Contextual Question (`tool_choice`: "answer_question")**
If the user asks a question about the video's content, asks for creative advice, or gives a vague command that requires visual context to understand, you must choose this path. This path will require analyzing the video's content.

*   **Examples of Contextual Questions:**
    *   "What is this video about?"
    *   "How can I make the intro more exciting?"
    *   "Cut the part where the man is smiling." (Requires vision to find the time)
    *   "Add a title card that matches the video's aesthetic."

*   **JSON Format for `contextual_question`:**
    ```json
    {
      "tool_choice": "answer_question",
      "data": {
        "question": "The user's original query"
      }
    }
    ```

You MUST respond with a single JSON object. Do not add any conversational text. Your primary job is to be an efficient router.
"""

def chatbot(state: GraphState):
    """
    Acts as the brain of the graph. It parses the user's query using an LLM
    and formats it into a structured JSON for downstream tasks.
    """
    
    # Initialize the chatbot model
    model = ChatOpenAI(temperature=0, streaming=True, model_kwargs={"response_format": {"type": "json_object"}})
    
    query = state.get("query")
    video_description = state.get("video_description", "No description available.")

    if not query:
        return {**state, "error": "Query is missing"}

    # Construct a dynamic prompt that includes the video description
    prompt_with_context = f"""{SYSTEM_PROMPT}

Here is the description of the current video:
---
{video_description}
---
"""

    # Create the message list with the system prompt and user query
    messages: List[BaseMessage] = [
        SystemMessage(content=prompt_with_context),
        HumanMessage(content=query)
    ]
    
    # Get the AI's response
    response = model.invoke(messages)
    
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
