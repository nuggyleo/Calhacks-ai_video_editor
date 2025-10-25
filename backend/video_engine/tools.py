from langchain_core.tools import tool
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.fx import all as vfx
from typing import Optional
from pathlib import Path
import uuid
import json
from backend.ai_services.filter_mapper import map_description_to_filter

# Define the output directory relative to this file's location
# tools.py -> video_engine -> backend -> [project_root]
OUTPUT_DIR = Path(__file__).parent.parent.parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def get_output_path(input_path: str, suffix: str) -> str:
    """Creates a unique output path in the designated OUTPUT_DIR."""
    original_filename = Path(input_path).stem
    unique_id = uuid.uuid4().hex[:8]
    new_filename = f"{original_filename}_{suffix}_{unique_id}.mp4"
    return str(OUTPUT_DIR / new_filename)


@tool
def trim_video(video_path: str, start_time: float, end_time: Optional[float] = None) -> str:
    """
    Trims a video to a specified start and end time.
    :param video_path: str, the file path of the input video.
    :param start_time: float, the start time in seconds for the trim.
    :param end_time: Optional[float], the end time in seconds for the trim. If not provided, it trims to the end of the video.
    :return: str, the file path of the trimmed video.
    """
    with VideoFileClip(video_path) as clip:
        if end_time is None:
            end_time = clip.duration
        subclip = clip.subclip(start_time, end_time)
        output_path = get_output_path(video_path, "trimmed")
        subclip.write_videofile(output_path, codec="libx264")
    return output_path

@tool
def add_text_to_video(video_path: str, text: str, start_time: float, duration: float, position: str = "center", fontsize: int = 70, color: str = 'white') -> str:
    """
    Adds a text overlay to a video at a specific time.
    :param video_path: str, the file path of the input video.
    :param text: str, the text content to add.
    :param start_time: float, the time in seconds when the text should appear.
    :param duration: float, how long the text should stay on screen in seconds.
    :param position: str, the position of the text (e.g., 'center', 'top', 'bottom').
    :param fontsize: int, the font size of the text.
    :param color: str, the color of the text.
    :return: str, the file path of the video with the text overlay.
    """
    with VideoFileClip(video_path) as clip:
        text_clip = TextClip(text, fontsize=fontsize, color=color).set_position(position).set_start(start_time).set_duration(duration)
        final_clip = CompositeVideoClip([clip, text_clip])
        output_path = get_output_path(video_path, "text_added")
        final_clip.write_videofile(output_path, codec="libx264")
    return output_path

@tool
def apply_filter_to_video(video_path: str, filter_description: str) -> str:
    """
    Applies a visual filter to the entire video based on a natural language description.
    For example, 'make the video black and white' or 'darken the video by 10%'.
    :param video_path: str, the file path of the input video.
    :param filter_description: str, a natural language description of the filter to apply.
    :return: str, the file path of the filtered video.
    """
    filter_info = map_description_to_filter(filter_description)
    filter_name = filter_info.get("filter_name")
    parameters = filter_info.get("parameters", {})

    if not hasattr(vfx, filter_name):
        raise ValueError(f"Filter '{filter_name}' not found in moviepy.video.fx.all")

    with VideoFileClip(video_path) as clip:
        filter_func = getattr(vfx, filter_name)
        final_clip = clip.fx(filter_func, **parameters)
        
        output_path = get_output_path(video_path, filter_name)
        final_clip.write_videofile(output_path, codec="libx264")
    return output_path

@tool
def change_video_speed(video_path: str, speed_factor: float) -> str:
    """
    Changes the speed of the video.
    :param video_path: str, the file path of the input video.
    :param speed_factor: float, the factor by which to change the speed. >1 for speed up, <1 for slow down.
    :return: str, the file path of the speed-adjusted video.
    """
    with VideoFileClip(video_path) as clip:
        final_clip = clip.speedx(speed_factor)
        output_path = get_output_path(video_path, f"speed_{speed_factor}x")
        final_clip.write_videofile(output_path, codec="libx264")
    return output_path
