from moviepy.editor import VideoFileClip, concatenate_videoclips
from typing import List

def split_video(
    video_path: str, start_time: float, end_time: float
) -> VideoFileClip:
    """
    Splits a video clip from a start time to an end time.

    Args:
        video_path: The path to the video file.
        start_time: The start time of the subclip in seconds.
        end_time: The end time of the subclip in seconds.

    Returns:
        A video clip object representing the subclip.
    """
    clip = VideoFileClip(video_path)
    return clip.subclip(start_time, end_time)


def concatenate_videos(
    clips: List[VideoFileClip], output_path: str, method: str = "compose"
):
    """
    Concatenates a list of video clips into a single video.

    Args:
        clips: A list of video clip objects to concatenate.
        output_path: The path to save the concatenated video.
        method: The method to use for concatenation ('compose' or 'chain').
    """
    final_clip = concatenate_videoclips(clips, method=method)
    final_clip.write_videofile(output_path)
