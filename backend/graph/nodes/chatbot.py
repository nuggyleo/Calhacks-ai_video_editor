from typing import List
import json
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from backend.graph.state import GraphState

# This is the new, powerful prompt for our chatbot.
# It instructs the AI on its role, capabilities, and the JSON output format.
SYSTEM_PROMPT = """You are an expert video editing assistant. Your goal is to understand the user's request and translate it into a structured JSON format that can be used to execute video editing tasks or answer questions.

**Video Context:**
You will be provided with a summary of the video's content. Use this context to answer any questions the user might have about the video. If the user's question is not related to the video content, you can answer it generally.

**Your Capabilities:**
1.  **Answer Questions**: If the user asks a question, identify it and format it as a 'question' type. Use the provided video context to answer questions about the video.
2.  **Video Editing**: You can perform the following edits:
    *   `trim`: Cut the video to a specific start and end time.
    *   `add_text`: Add text overlays to the video.
    *   `apply_filter`: Apply visual filters like 'grayscale' or 'sepia'.
    *   `set_audio`: Replace the video's audio with a new audio file.

**Output Format:**
You MUST respond with a single JSON object. Do not add any conversational text or explanations outside of the JSON. The JSON object should have two keys: "type" and "data".

1.  If the user asks a question (e.g., "Hi", "What can you do?", "How does this work?"):
    ```json
    {
      "type": "question",
      "data": {
        "question": "The user's original question"
      }
    }
    ```

2.  If the user requests a video edit:
    ```json
    {
      "type": "edit",
      "data": [
        {
          "action": "action_name",
          ...action_specific_parameters
        }
      ]
    }
    ```

**Examples of Edit Requests:**

*   **User:** "Trim the video from 10 seconds to 30 seconds."
    ```json
    {
      "type": "edit",
      "data": [
        {
          "action": "trim",
          "start_time": 10,
          "end_time": 30
        }
      ]
    }
    ```

*   **User:** "Add the text 'Hello World' at the top of the screen."
    ```json
    {
      "type": "edit",
      "data": [
        {
          "action": "add_text",
          "text": "Hello World",
          "position": "top" 
        }
      ]
    }
    ```

*   **User:** "Make the video black and white."
    ```json
    {
      "type": "edit",
      "data": [
        {
          "action": "apply_filter",
          "filter_type": "grayscale"
        }
      ]
    }
    ```
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
        
        # Update the state with the parsed query.
        # This 'parsed_query' will be used by the 'query_parser' node to route.
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
