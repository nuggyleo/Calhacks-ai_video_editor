# This file will focus on advanced audio manipulation within a video project.
# It will handle tasks beyond simply adding a background track, such as
# noise reduction, volume automation, and audio mixing.
#
# These functions will use FFmpeg's powerful audio filters.
#
# Example Functions:
# - `reduce_noise(input_path: str, output_path: str)`:
#   Applies a noise reduction filter to the audio track.
#
# - `duck_audio(main_track_path: str, duck_track_path: str, output_path: str)`:
#   Lowers the volume of the `duck_track` (e.g., music) whenever there is
#   audio in the `main_track` (e.g., dialogue). This is known as "audio ducking".

from moviepy.editor import VideoClip, AudioFileClip

def set_audio(clip: VideoClip, audio_path: str) -> VideoClip:
    """
    Replaces the audio of a video clip with a new audio file.

    Args:
        clip: The video clip to modify.
        audio_path: The path to the new audio file.

    Returns:
        A new video clip with the replaced audio.
    """
    audio_clip = AudioFileClip(audio_path)
    new_clip = clip.set_audio(audio_clip)
    return new_clip
