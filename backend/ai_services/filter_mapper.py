import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json

def map_description_to_filter(description: str):
    """
    Maps a natural language description to a corresponding moviepy filter and its parameters.
    """
    
    # A curated list of available filters and their accepted parameters.
    # This helps the model to not hallucinate parameters.
    available_filters = {
        "blackwhite": [],
        "invert_colors": [],
        "fadein": ["duration"],
        "fadeout": ["duration"],
        "multiply_color": ["factor"],
        "lum_contrast": ["lum", "contrast", "contrast_thr"],
        "speedx": ["factor"],
        "rotate": ["angle"],
        "resize": ["width", "height"],
        "crop": ["x1", "y1", "x2", "y2"],
    }
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
            You are an expert in video editing and the moviepy library. Your task is to map a user's natural language description of a filter to the most appropriate moviepy filter and its parameters from the provided list.

            **Available Filters and Parameters:**
            ```json
            {filters}
            ```

            **Your Task:**
            1.  Analyze the user's request: "{description}"
            2.  Choose the best matching filter from the list.
            3.  Determine the correct parameters for the filter based on the user's request. **Only use the parameters listed for each filter.** Do not invent new ones.
            4.  If the user wants to apply a color tint (e.g., "make it green", "add a blue filter"), use the `multiply_color` filter with an RGB `factor`. For example, a green filter would be `[0, 1, 0]`. A red filter would be `[1, 0, 0]`.
            5.  Your response must be a JSON object with two keys: "filter_name" and "parameters". If no parameters are needed, provide an empty object.

            **Example 1:**
            User Request: "make it black and white"
            Response:
            {{
                "filter_name": "blackwhite",
                "parameters": {{}}
            }}

            **Example 2:**
            User Request: "add a strong green tint"
            Response:
            {{
                "filter_name": "multiply_color",
                "parameters": {{ "factor": [0, 1.5, 0] }}
            }}
        """),
        ("human", "{description}")
    ])
    
    model = ChatOpenAI(temperature=0)
    parser = JsonOutputParser()
    
    chain = prompt | model | parser
    
    return chain.invoke({
        "filters": json.dumps(available_filters, indent=2),
        "description": description
    })
