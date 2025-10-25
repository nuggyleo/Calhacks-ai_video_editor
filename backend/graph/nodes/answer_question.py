# This node is responsible for answering the user's question.
# It takes the user's question and the video content as input.
# It should generate a helpful answer based on the video content.

from backend.graph.state import GraphState
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def answer_question(state: GraphState):
    """
    Answers a question based on the parsed query and the video description from the state.
    """
    print("---ANSWERING QUESTION (ADAPTIVE AI)---")
    parsed_query = state.get("parsed_query", {})
    question = parsed_query.get("data", {}).get("question", "Could not find question.")
    video_description = state.get("video_description", "No description was provided for the video.")

    # A more advanced prompt that adapts its persona based on the user's question.
    prompt = f"""You are an expert AI video editing assistant. Your primary goal is to assist users helpfully and concisely. You have three modes of response based on the user's intent.

    **1. General Conversation Mode:**
    If the user's query is a simple greeting (e.g., "Hi", "Hello"), a sign-off ("Thanks!"), or a general conversational turn that doesn't fit the other modes, respond as a friendly and helpful assistant. Keep your response brief and natural. Do not offer editing advice unless asked. Be sure to remember your role, when the user asks what can you do, summarize the work that you can achieve. 

    **2. Content Inquiry Mode:**
    If the user asks a direct, factual question about the video's content (e.g., "What is this video about?", "Summarize this clip."), your task is to provide a concise and direct summary based *only* on the provided "Video Description". If no description is available, politely state that you cannot see the video content.

    **3. Creative Consultation Mode:**
    If the user asks for editing advice, ideas, or suggestions (e.g., "How can I make this more exciting?", "What music should I use?"), then you must act as a creative partner. Use your guiding principles to provide insightful, constructive, and actionable advice.

    **Your Guiding Principles (for Creative Consultation Mode only):**
    *   Story is King: Focus on the narrative.
    *   Pacing and Rhythm: Control the video's flow.
    *   Visual Interest: Keep the viewer engaged.
    *   Emotional Impact: Evoke the desired feeling.

    ---
    **Your Task:**
    First, determine the user's intent from their question. Then, respond in the appropriate mode based on the video description and the user's question below.

    **Video Description:**
    ---
    {video_description}
    ---

    **User's Question:**
    "{question}"

    Provide your response below.
    """
    
    # Model invocation with a balanced temperature for both factual and creative tasks.
    model = ChatOpenAI(temperature=0.4)
    response = model.invoke([HumanMessage(content=prompt)])
    
    # Return the response as a message to be appended to the history
    return {"messages": [AIMessage(content=response.content)]}
