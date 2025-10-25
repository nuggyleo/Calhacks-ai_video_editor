import re

def map_description_to_filter(description: str):
    """
    Maps a natural language description to a corresponding moviepy filter and its parameters
    using a more comprehensive, hard-coded mapping.
    """
    desc = description.lower()
    
    # --- Simple Filters (no parameters needed) ---
    if "black and white" in desc or "grayscale" in desc:
        return {"filter_name": "blackwhite", "parameters": {}}
    if "invert" in desc:
        return {"filter_name": "invert_colors", "parameters": {}}
    if "mirror x" in desc or "flip horizontally" in desc:
        return {"filter_name": "mirror_x", "parameters": {}}
    if "mirror y" in desc or "flip vertically" in desc:
        return {"filter_name": "mirror_y", "parameters": {}}

    # --- Filters with Numerical Parameters ---
    # Fade In/Out - now accepts "second" or "seconds"
    fade_match = re.search(r"fade (in|out) for (\d+\.?\d*) second(s)?", desc)
    if fade_match:
        direction, duration = fade_match.groups()[0:2] # Ignore the optional 's'
        return {
            "filter_name": f"fade{direction}",
            "parameters": {"duration": float(duration)}
        }
    
    # Brightness/Contrast
    if "darken" in desc or "brightness down" in desc:
        return {"filter_name": "lum_contrast", "parameters": {"lum": -3}}
    if "brighten" in desc or "brightness up" in desc:
        return {"filter_name": "lum_contrast", "parameters": {"lum": 3}}
    
    # Color Tints - now correctly uses "MultiplyColor"
    if "sepia" in desc:
        return {"filter_name": "MultiplyColor", "parameters": {"factor": [1.5, 1.1, 0.9]}}
    if "green" in desc:
        return {"filter_name": "MultiplyColor", "parameters": {"factor": [0, 1.3, 0]}}
    if "blue" in desc:
        return {"filter_name": "MultiplyColor", "parameters": {"factor": [0, 0, 1.3]}}
    if "red" in desc:
        return {"filter_name": "MultiplyColor", "parameters": {"factor": [1.3, 0, 0]}}

    # Rotate
    rotate_match = re.search(r"rotate by (\d+\.?\d*) degrees", desc)
    if rotate_match:
        angle = rotate_match.groups()[0]
        return {"filter_name": "rotate", "parameters": {"angle": float(angle)}}

    # Fallback for unsupported filters
    raise ValueError(f"Filter description '{description}' is not supported or is incorrectly formatted.")
