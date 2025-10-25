import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv

load_dotenv()

def map_description_to_filter(description: str):
    """
    Dynamically maps a natural language description to a corresponding moviepy filter
    and its parameters by calling an AI model.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")

    # The AI will act as a video engineer to parse the request
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are an expert video engineer. Your task is to parse a user's natural language request and convert it into a filter name and parameters for our video editing tool.
        
        Our tool uses a stable OpenCV backend. The filter name you provide must be one of the keys in our supported filter dictionary.

        You must return the output in a JSON object with two keys:
        1.  `"filter_name"`: A string with the exact, lowercase name of one of our supported filters.
        2.  `"parameters"`: A JSON object of the parameters for that filter. If no parameters are needed, return an empty object `{{}}`.

        Here is the list of supported filters and their parameters:
        - `blackwhite`: {{}}
        - `sepia`: {{}}
        - `lum_contrast`: `{{"lum": int, "contrast": int}}` (lum is brightness, contrast is contrast)
        - `blur`: `{{"ksize": [width, height]}}` (e.g., [15, 15] for a strong blur)
        - `gaussian_blur`: `{{"ksize": [width, height], "sigmaX": float}}`
        - `median_blur`: `{{"ksize": int}}` (e.g., 15 for a strong blur)
        - `color_tint`: `{{"color": "red"}}` (can be "red", "green", or "blue")
        - `fadein`: `{{"duration": float}}` (duration in seconds, defaults to 3s if not specified)
        - `fadeout`: `{{"duration": float}}` (duration in seconds, defaults to 3s if not specified)

        The user's request may be slightly ambiguous. Make a best-effort attempt to map it to the most logical filter and parameters.
        For example:
        - "make it black and white" should map to `{{"filter_name": "blackwhite", "parameters": {{}} }}`.
        - "add a strong blur" should map to `{{"filter_name": "blur", "parameters": {{"ksize": [25, 25]}} }}`.
        - "increase the brightness" should map to `{{"filter_name": "lum_contrast", "parameters": {{"lum": 50, "contrast": 0}} }}`.
        - "give it a red tint" should map to `{{"filter_name": "color_tint", "parameters": {{"color": "red"}} }}`.
        - "fade in" should map to `{{"filter_name": "fadein", "parameters": {{"duration": 3.0}} }}`.
        - "fade out for 5 seconds" should map to `{{"filter_name": "fadeout", "parameters": {{"duration": 5.0}} }}`.
        """),
        ("human", "Parse the following filter description: '{description}'")
    ])

    # The model will generate a JSON string, which we parse into a Python dict
    llm = ChatOpenAI(temperature=0, model="gpt-4-turbo-preview", openai_api_key=api_key)
    parser = JsonOutputParser()
    chain = prompt | llm | parser

    # Invoke the chain and get the structured output
    result = chain.invoke({"description": description})
    return result
