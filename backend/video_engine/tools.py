from langchain_core.tools import tool
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from typing import Optional

# Note: For this agent-based approach, our tools will operate on file paths.
# The agent will receive an input video path and must return a new output video path for each step.
# This makes the process stateless and easier for the LLM to manage.

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
        output_path = video_path.replace(".mp4", f"_trimmed_{start_time}_{end_time}.mp4")
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
        output_path = video_path.replace(".mp4", f"_text_added.mp4")
        final_clip.write_videofile(output_path, codec="libx264")
    return output_path

@tool
def apply_filter_to_video(video_path: str, filter_type: str) -> str:
    """
    Applies a visual filter to the entire video.
    Supported filters are: 'grayscale', 'invert_colors'.
    :param video_path: str, the file path of the input video.
    :param filter_type: str, the type of filter to apply. Must be one of ['grayscale', 'invert_colors'].
    :return: str, the file path of the filtered video.
    """
    with VideoFileClip(video_path) as clip:
        if filter_type == 'grayscale':
            # Example of applying a grayscale effect
            final_clip = clip.fx(vfx.blackwhite)
        elif filter_type == 'invert_colors':
            # Example of inverting colors
            final_clip = clip.fx(vfx.invert_colors)
        else:
            raise ValueError(f"Unsupported filter type: {filter_type}. Supported filters are 'grayscale', 'invert_colors'.")
        
        output_path = video_path.replace(".mp4", f"_{filter_type}.mp4")
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
        output_path = video_path.replace(".mp4", f"_speed_{speed_factor}x.mp4")
        final_clip.write_videofile(output_path, codec="libx264")
    return output_path
