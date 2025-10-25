from moviepy.editor import VideoClip, TextClip, CompositeVideoClip
import moviepy.video.fx.all as vfx

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
