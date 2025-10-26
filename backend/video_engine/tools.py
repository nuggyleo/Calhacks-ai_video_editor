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
from backend.video_engine.editing.effects import apply_effects # <-- Import the robust function

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
    try:
        video_path = resolve_video_path(active_video_id, media_bin)
        logger.info(f"Resolved video path: {video_path}")
        
        with VideoFileClip(video_path) as clip:
            # Validate end_time against the clip's duration
            actual_end_time = end_time if end_time is not None else clip.duration
            if start_time >= clip.duration or actual_end_time > clip.duration:
                return f"Error: Invalid trim time. Start ({start_time}s) or end ({actual_end_time}s) is beyond the video duration ({clip.duration}s)."

            subclip = clip.subclip(start_time, actual_end_time)
            output_path = get_output_path(video_path, "trimmed")
            
            logger.info(f"Writing trimmed video to: {output_path}")
            subclip.write_videofile(output_path, codec="libx264", logger='bar')
            
        logger.info(f"--- TOOL: trim_video finished ---")
        return output_path
    except Exception as e:
        logger.error(f"An unexpected error occurred in trim_video: {e}")
        return f"Error: An unexpected error occurred while trimming the video. Please check the start and end times."

@tool
def add_text_to_video(active_video_id: str, media_bin: Dict[str, str], text: str, start_time: float, duration: float, position: str = "center", fontsize: int = 70, color: str = 'white') -> str:
    """
    Adds a text overlay to a video at a specific time.
    """
    logger.info(f"--- TOOL: add_text_to_video starting ---")
    try:
        from moviepy.config import get_setting
        if not get_setting("IMAGEMAGICK_BINARY"):
            logger.error("ImageMagick is not installed or configured.")
            return "Error: ImageMagick is not installed. Please install it to add text to videos."

        video_path = resolve_video_path(active_video_id, media_bin)
        logger.info(f"Resolved video path for text addition: {video_path}")
        
        with VideoFileClip(video_path) as clip:
            logger.info(f"Video clip for text addition loaded successfully. Duration: {clip.duration}s")
            
            # Ensure the clip has a size, which is necessary for TextClip positioning
            if clip.size is None:
                raise ValueError("The video clip does not have a defined size.")
            
            logger.info(f"Clip size: {clip.size}")

            text_clip = TextClip(txt=text, fontsize=fontsize, color=color, size=clip.size).set_position(position).set_start(start_time).set_duration(duration)
            logger.info(f"Text clip created successfully.")

            final_clip = CompositeVideoClip([clip, text_clip])
            logger.info(f"Composite clip created successfully.")

            output_path = get_output_path(video_path, "text_added")

            logger.info(f"Writing video with text to: {output_path}")
            final_clip.write_videofile(output_path, codec="libx264", logger='bar')
            
        logger.info(f"--- TOOL: add_text_to_video finished ---")
        return output_path
    except Exception as e:
        logger.error(f"An unexpected error occurred in add_text_to_video: {e}", exc_info=True)
        return f"Error: An unexpected error occurred while adding text to the video: {str(e)}"

@tool
def apply_filter_to_video(active_video_id: str, media_bin: Dict[str, str], filter_description: str) -> str:
    """
    Applies a visual filter to the entire video based on a natural language description.
    Returns the path to the new video file on success, or an error message on failure.
    """
    logger.info(f"--- TOOL: apply_filter_to_video starting ---")
    
    try:
        video_path = resolve_video_path(active_video_id, media_bin)
        logger.info(f"Resolved video path: {video_path}")
        
        filter_info = map_description_to_filter(filter_description)
        logger.info(f"Filter mapping result: {filter_info}")
        filter_name = filter_info.get("filter_name")
        parameters = filter_info.get("parameters", {})
        logger.info(f"Filter name: {filter_name}, Parameters: {parameters}")

        with VideoFileClip(video_path) as clip:
            # Use the robust apply_effects function
            final_clip = apply_effects(clip, filter_name, **parameters)
            
            output_path = get_output_path(video_path, filter_name)
            logger.info(f"Writing filtered video to: {output_path}")
            final_clip.write_videofile(output_path, codec="libx264", logger='bar')
            
        logger.info(f"--- TOOL: apply_filter_to_video finished ---")
        return output_path

    except ValueError as e:
        # This catches errors from apply_effects for unsupported filters
        logger.warning(f"Filter not supported: {e}")
        return f"Error: The requested filter ('{filter_description}') is not supported. Please try a different effect."
    except Exception as e:
        # Catch any other unexpected errors during the process
        logger.error(f"An unexpected error occurred in apply_filter_to_video: {e}")
        return f"Error: An unexpected error occurred while applying the filter. Please try again."

@tool
def change_video_speed(active_video_id: str, media_bin: Dict[str, str], speed_factor: float) -> str:
    """
    Changes the speed of the video.
    """
    logger.info(f"--- TOOL: change_video_speed starting ---")
    try:
        video_path = resolve_video_path(active_video_id, media_bin)
        logger.info(f"Resolved video path: {video_path}")
        
        with VideoFileClip(video_path) as clip:
            final_clip = clip.speedx(speed_factor)
            output_path = get_output_path(video_path, f"speed_{speed_factor}x")
            
            logger.info(f"Writing speed-adjusted video to: {output_path}")
            final_clip.write_videofile(output_path, codec="libx264", logger='bar')
            
        logger.info(f"--- TOOL: change_video_speed finished ---")
        return output_path
    except Exception as e:
        logger.error(f"An unexpected error occurred in change_video_speed: {e}")
        return "Error: An unexpected error occurred while changing the video speed."

@tool
def extract_audio(active_video_id: str, media_bin: Dict[str, str]) -> str:
    """
    Extracts the audio track from a video and saves it as an MP3 file.
    It adds the new audio file to the media bin and returns the new audio_id.
    """
    logger.info(f"--- TOOL: extract_audio starting ---")
    video_path = resolve_video_path(active_video_id, media_bin)
    logger.info(f"Resolved video path: {video_path}")
    
    with VideoFileClip(video_path) as clip:
        if clip.audio is None:
            raise ValueError("The video does not have an audio track.")
        
        # 1. Generate a unique ID and path for the new audio file
        audio_id = str(uuid.uuid4())
        output_path = get_output_path(video_path, "extracted_audio", extension="mp3")
        
        logger.info(f"Writing extracted audio to: {output_path}")
        clip.audio.write_audiofile(output_path, logger='bar')
        
        # 2. Add the new audio file to the media bin
        # NOTE: This modifies the dictionary in-place.
        media_bin[audio_id] = output_path
        logger.info(f"Added new audio '{audio_id}' to media bin.")
        
    logger.info(f"--- TOOL: extract_audio finished ---")
    # 3. Return the new audio_id
    return audio_id

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

    moviepy_clips = [] # Define here to be accessible in finally block
    try:
        video_paths = [media_bin.get(vid_id) for vid_id in video_ids]
        if not all(video_paths):
            missing_ids = [vid_id for vid_id, path in zip(video_ids, video_paths) if not path]
            raise ValueError(f"Could not find video paths for the following IDs: {missing_ids}")

        logger.info(f"Resolved video paths: {video_paths}")

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
        
        logger.info(f"--- TOOL: concatenate_videos finished ---")
        return output_path

    except Exception as e:
        logger.error(f"Error during video concatenation: {e}")
        return f"Error: An unexpected error occurred during video concatenation: {e}"
    finally:
        # Clean up all original video file clips
        for clip in moviepy_clips:
            clip.close()
        if 'final_clip' in locals() and 'final_clip' is not None:
            final_clip.close()

@tool
def extract_and_add_audio(source_video_id: str, destination_video_id: str, media_bin: Dict[str, str]) -> str:
    """
    Extracts audio from a source video and adds it to a destination video in a single operation.
    """
    logger.info(f"--- TOOL: extract_and_add_audio starting ---")
    logger.info(f"Source video: {source_video_id}, Destination video: {destination_video_id}")

    try:
        # 1. Resolve paths
        source_path = resolve_video_path(source_video_id, media_bin)
        destination_path = resolve_video_path(destination_video_id, media_bin)
        logger.info(f"Resolved source path: {source_path}")
        logger.info(f"Resolved destination path: {destination_path}")

        # 2. Perform the combined operation
        with VideoFileClip(source_path) as source_clip, VideoFileClip(destination_path) as dest_clip:
            if source_clip.audio is None:
                raise ValueError(f"The source video ('{source_video_id}') has no audio track to extract.")
            
            # Set the destination clip's audio to the source clip's audio
            final_clip = dest_clip.set_audio(source_clip.audio)
            
            output_path = get_output_path(destination_path, "audio_swapped")
            
            logger.info(f"Writing final video to: {output_path}")
            final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", logger='bar')

        logger.info(f"--- TOOL: extract_and_add_audio finished ---")
        return output_path

    except Exception as e:
        logger.error(f"Error during extract_and_add_audio: {e}", exc_info=True)
        return f"Error: Failed to extract and add audio. Details: {str(e)}"
