import logging
from langchain_core.tools import tool
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
    ColorClip,
)
import moviepy.video.fx.all as vfx
from typing import Optional, Dict, List
from pathlib import Path
import uuid
import json
from backend.ai_services.filter_mapper import map_description_to_filter

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the output directory relative to this file's location
# tools.py -> video_engine -> backend -> [project_root]
OUTPUT_DIR = Path(__file__).parent.parent.parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


def get_output_path(input_path: str, suffix: str, extension: str = "mp4") -> str:
    """Creates a unique output path in the designated OUTPUT_DIR."""
    original_filename = Path(input_path).stem
    unique_id = uuid.uuid4().hex[:8]
    new_filename = f"{original_filename}_{suffix}_{unique_id}.{extension}"
    return str(OUTPUT_DIR / new_filename)


def resolve_video_path(active_video_id: str, media_bin: Dict[str, str]) -> str:
    """Looks up the video path from the media bin."""
    if active_video_id not in media_bin:
        raise ValueError(f"Video ID '{active_video_id}' not found in the media bin.")
    return media_bin[active_video_id]

@tool
def trim_video(active_video_id: str, media_bin: Dict[str, str], start_time: float, end_time: Optional[float] = None) -> str:
    """
    Trims a video to a specified start and end time.
    """
    logger.info(f"--- TOOL: trim_video starting ---")
    video_path = resolve_video_path(active_video_id, media_bin)
    logger.info(f"Resolved video path: {video_path}")
    
    with VideoFileClip(video_path) as clip:
        if end_time is None:
            end_time = clip.duration
        subclip = clip.subclip(start_time, end_time)
        output_path = get_output_path(video_path, "trimmed")
        
        logger.info(f"Writing trimmed video to: {output_path}")
        subclip.write_videofile(output_path, codec="libx264", logger='bar')
        
    logger.info(f"--- TOOL: trim_video finished ---")
    return output_path

@tool
def add_text_to_video(active_video_id: str, media_bin: Dict[str, str], text: str, start_time: float, duration: float, position: str = "center", fontsize: int = 70, color: str = 'white') -> str:
    """
    Adds a text overlay to a video at a specific time.
    """
    logger.info(f"--- TOOL: add_text_to_video starting ---")
    video_path = resolve_video_path(active_video_id, media_bin)
    logger.info(f"Resolved video path: {video_path}")
    
    with VideoFileClip(video_path) as clip:
        text_clip = TextClip(text, fontsize=fontsize, color=color).set_position(position).set_start(start_time).set_duration(duration)
        final_clip = CompositeVideoClip([clip, text_clip])
        output_path = get_output_path(video_path, "text_added")

        logger.info(f"Writing video with text to: {output_path}")
        final_clip.write_videofile(output_path, codec="libx264", logger='bar')
        
    logger.info(f"--- TOOL: add_text_to_video finished ---")
    return output_path

@tool
def apply_filter_to_video(active_video_id: str, media_bin: Dict[str, str], filter_description: str) -> str:
    """
    Applies a visual filter to the entire video based on a natural language description.
    """
    logger.info(f"--- TOOL: apply_filter_to_video starting ---")
    video_path = resolve_video_path(active_video_id, media_bin)
    logger.info(f"Resolved video path: {video_path}")
    
    filter_info = map_description_to_filter(filter_description)
    filter_name = filter_info.get("filter_name")
    parameters = filter_info.get("parameters", {})

    if not hasattr(vfx, filter_name):
        raise ValueError(f"Filter '{filter_name}' not found in moviepy.video.fx.all")

    with VideoFileClip(video_path) as clip:
        filter_func = getattr(vfx, filter_name)
        final_clip = clip.fx(filter_func, **parameters)
        
        output_path = get_output_path(video_path, filter_name)
        logger.info(f"Writing filtered video to: {output_path}")
        final_clip.write_videofile(output_path, codec="libx264", logger='bar')
        
    logger.info(f"--- TOOL: apply_filter_to_video finished ---")
    return output_path

@tool
def change_video_speed(active_video_id: str, media_bin: Dict[str, str], speed_factor: float) -> str:
    """
    Changes the speed of the video.
    """
    logger.info(f"--- TOOL: change_video_speed starting ---")
    video_path = resolve_video_path(active_video_id, media_bin)
    logger.info(f"Resolved video path: {video_path}")
    
    with VideoFileClip(video_path) as clip:
        final_clip = clip.speedx(speed_factor)
        output_path = get_output_path(video_path, f"speed_{speed_factor}x")
        
        logger.info(f"Writing speed-adjusted video to: {output_path}")
        final_clip.write_videofile(output_path, codec="libx264", logger='bar')
        
    logger.info(f"--- TOOL: change_video_speed finished ---")
    return output_path

@tool
def extract_audio(active_video_id: str, media_bin: Dict[str, str]) -> str:
    """
    Extracts the audio track from a video and saves it as an MP3 file.
    Returns the path to the extracted audio file.
    """
    logger.info(f"--- TOOL: extract_audio starting ---")
    video_path = resolve_video_path(active_video_id, media_bin)
    logger.info(f"Resolved video path: {video_path}")
    
    with VideoFileClip(video_path) as clip:
        if clip.audio is None:
            raise ValueError("The video does not have an audio track.")
        
        output_path = get_output_path(video_path, "extracted_audio", extension="mp3")
        
        logger.info(f"Writing extracted audio to: {output_path}")
        clip.audio.write_audiofile(output_path, logger='bar')
        
    logger.info(f"--- TOOL: extract_audio finished ---")
    return output_path

@tool
def add_audio_to_video(video_id: str, audio_id: str, media_bin: Dict[str, str]) -> str:
    """
    Replaces or adds an audio track to a video. The audio can be from an audio file in the media bin.
    
    Args:
        video_id: The ID of the video to add audio to.
        audio_id: The ID of the audio file in the media bin.
        media_bin: Dictionary mapping media IDs to file paths.
    
    Returns:
        Path to the new video file with the audio track.
    """
    logger.info(f"--- TOOL: add_audio_to_video starting ---")
    
    if video_id not in media_bin:
        raise ValueError(f"Video ID '{video_id}' not found in the media bin.")
    if audio_id not in media_bin:
        raise ValueError(f"Audio ID '{audio_id}' not found in the media bin.")
    
    video_path = media_bin[video_id]
    audio_path = media_bin[audio_id]
    
    logger.info(f"Video path: {video_path}")
    logger.info(f"Audio path: {audio_path}")
    
    with VideoFileClip(video_path) as video_clip:
        with AudioFileClip(audio_path) as audio_clip:
            # Set the audio of the video clip
            final_clip = video_clip.set_audio(audio_clip)
            
            output_path = get_output_path(video_path, "with_audio")
            
            logger.info(f"Writing video with new audio to: {output_path}")
            final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", logger='bar')
    
    logger.info(f"--- TOOL: add_audio_to_video finished ---")
    return output_path

@tool
def concatenate_videos(video_ids: List[str], media_bin: Dict[str, str]) -> str:
    """
    Concatenates multiple videos together in the specified order.
    :param video_ids: list[str], a list of the video IDs to concatenate.
    :param media_bin: Dict[str, str], the media bin containing the video paths.
    :return: str, the file path of the new concatenated video.
    """
    logger.info(f"--- TOOL: concatenate_videos starting ---")
    logger.info(f"Received video IDs for concatenation: {video_ids}")

    video_paths = [media_bin.get(vid_id) for vid_id in video_ids]
    if not all(video_paths):
        missing_ids = [vid_id for vid_id, path in zip(video_ids, video_paths) if not path]
        raise ValueError(f"Could not find video paths for the following IDs: {missing_ids}")

    logger.info(f"Resolved video paths: {video_paths}")

    try:
        # Load clips into moviepy objects
        moviepy_clips = [VideoFileClip(path) for path in video_paths]

        # --- NEW: Intelligent resizing with padding to preserve quality ---
        # 1. Find the maximum resolution among all clips
        max_width = max(clip.w for clip in moviepy_clips)
        max_height = max(clip.h for clip in moviepy_clips)
        target_size = (max_width, max_height)
        logger.info(f"Standardizing all clips to max resolution: {target_size} by padding smaller clips.")

        # 2. Add padding to smaller clips to match the max resolution
        processed_clips = []
        for clip in moviepy_clips:
            if clip.size != target_size:
                # Create a black background clip of the target size
                background = ColorClip(size=target_size, color=(0,0,0), duration=clip.duration)
                # Place the original clip in the center of the background
                padded_clip = CompositeVideoClip([background, clip.set_position('center')])
                processed_clips.append(padded_clip)
            else:
                processed_clips.append(clip)

        # 3. Trim end frames to prevent glitches (still a good practice)
        final_clips = [clip.subclip(0, clip.duration - 0.05) for clip in processed_clips]
        # --- End of new logic ---

        output_path = get_output_path(video_paths[0], "concatenated")

        logger.info(f"Writing concatenated video to: {output_path}")
        final_clip = concatenate_videoclips(final_clips, method="compose")
        final_clip.write_videofile(output_path, codec="libx264", logger='bar')
        
        # Clean up all original video file clips
        for clip in moviepy_clips:
            clip.close()
        final_clip.close()

    except Exception as e:
        logger.error(f"Error during video concatenation: {e}")
        # Clean up any clips that were opened
        for clip in moviepy_clips:
            if clip:
                clip.close()
        raise e

    logger.info(f"--- TOOL: concatenate_videos finished ---")
    return output_path
