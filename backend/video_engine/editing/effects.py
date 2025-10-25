from moviepy.editor import VideoClip, TextClip, CompositeVideoClip
import moviepy.video.fx.all as vfx

def apply_effects(clip: VideoClip, filter_name: str, **kwargs) -> VideoClip:
    """
    Applies an effect to a video clip, intelligently handling both standard
    fx filters and VideoClip methods.
    """
    # Special handling for MultiplyColor to ensure version compatibility
    if filter_name == "MultiplyColor":
        return clip.fl_image(lambda frame: frame * kwargs.get("factor", 1))

    # Effects that are known to be unstable without pre-loading
    unstable_effects = ["time_mirror"]

    if filter_name in unstable_effects:
        # Pre-load the clip's audio and mask to stabilize it, only if they exist
        if clip.audio:
            clip.audio = clip.audio.to_soundarray()
        if clip.mask:
            clip.mask = clip.mask.to_mask()

    # Check if the filter is a method of the clip itself (e.g., fadein, rotate)
    if hasattr(clip, filter_name):
        return getattr(clip, filter_name)(**kwargs)
    # Check if the filter is in the vfx module
    elif hasattr(vfx, filter_name):
        filter_func = getattr(vfx, filter_name)
        return clip.fx(filter_func, **kwargs)
    else:
        raise ValueError(f"Effect '{filter_name}' not found in moviepy.")

def apply_filter(clip: VideoClip, filter_name: str, **kwargs) -> VideoClip:
    """
    Applies a filter to a video clip.

    Args:
        clip: The video clip to apply the filter to.
        filter_name: The name of the filter to apply (e.g., 'colorx', 'fadein').
        **kwargs: The arguments for the filter.

    Returns:
        The video clip with the filter applied.
    """
    if hasattr(vfx, filter_name):
        filter_func = getattr(vfx, filter_name)
        return clip.fx(filter_func, **kwargs)
    else:
        raise ValueError(f"Filter '{filter_name}' not found in moviepy.video.fx.all")

def add_caption(
    clip: VideoClip,
    text: str,
    start_time: float,
    duration: float,
    fontsize: int = 24,
    color: str = "white",
    position: tuple = ("center", "bottom"),
) -> CompositeVideoClip:
    """
    Adds a caption to a video clip.
    """
    caption_clip = (
        TextClip(text, fontsize=fontsize, color=color)
        .set_position(position)
        .set_start(start_time)
        .set_duration(duration)
    )
    return CompositeVideoClip([clip, caption_clip])

def add_subtitle(
    clip: VideoClip,
    text: str,
    start_time: float,
    duration: float,
    fontsize: int = 24,
    color: str = "white",
    position: tuple = ("center", "bottom"),
) -> CompositeVideoClip:
    """
    Adds a subtitle to a video clip.

    Args:
        clip: The video clip to add the subtitle to.
        text: The text of the subtitle.
        start_time: The time to start showing the subtitle.
        duration: The duration to show the subtitle.
        fontsize: The font size of the subtitle.
        color: The color of the subtitle.
        position: The position of the subtitle.

    Returns:
        The video clip with the subtitle.
    """
    text_clip = (
        TextClip(text, fontsize=fontsize, color=color)
        .set_position(position)
        .set_start(start_time)
        .set_duration(duration)
    )
    return CompositeVideoClip([clip, text_clip])
