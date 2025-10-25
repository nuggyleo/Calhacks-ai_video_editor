# This file is dedicated to the final stage of video production: exporting and compression.
# It provides a set of functions to encode the final video with different quality settings,
# balancing file size and visual fidelity for various use cases.
#
# We will use FFmpeg's powerful encoding options to control parameters like bitrate,
# resolution, and the Constant Rate Factor (CRF) for H.264/H.265 codecs.
#
# Example Functions:
# - `export_for_web(input_path: str, output_path: str)`:
#   Compresses the video to a smaller file size, suitable for web streaming.
#   (e.g., 720p resolution, lower bitrate).
#
# - `export_for_hd(input_path: str, output_path: str)`:
#   Exports the video in high definition, preserving more quality for viewing on large screens.
#   (e.g., 1080p resolution, higher bitrate).
#
# - `export_with_custom_settings(...)`:
#   A generic function that could take specific parameters for fine-tuned control.

from moviepy.editor import VideoClip

def export_video(
    clip: VideoClip,
    output_path: str,
    fps: int = 30,
    codec: str = "libx264",
    audio_codec: str = "aac",
    bitrate: str = "5000k",
):
    """
    Exports a video clip to a file.

    Args:
        clip: The video clip to export.
        output_path: The path to save the exported video.
        fps: The frames per second of the output video.
        codec: The video codec to use.
        audio_codec: The audio codec to use.
        bitrate: The bitrate of the output video.
    """
    clip.write_videofile(
        output_path,
        fps=fps,
        codec=codec,
        audio_codec=audio_codec,
        bitrate=bitrate,
    )
