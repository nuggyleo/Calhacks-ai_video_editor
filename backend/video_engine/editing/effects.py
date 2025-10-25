import cv2
import numpy as np
from moviepy.editor import VideoClip, TextClip, CompositeVideoClip

# --- OpenCV Filter Implementations ---
# Each function takes a frame (NumPy array) and returns a modified frame.

def _apply_blackwhite(frame):
    """Converts a frame to black and white."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR) # Convert back to 3 channels for moviepy

def _apply_sepia(frame):
    """Applies a sepia tone effect."""
    kernel = np.array([[0.272, 0.534, 0.131],
                       [0.349, 0.686, 0.168],
                       [0.393, 0.769, 0.189]])
    sepia_frame = cv2.transform(frame, kernel)
    sepia_frame = np.clip(sepia_frame, 0, 255) # Ensure values are within display range
    return sepia_frame.astype('uint8')

def _adjust_lum_contrast(frame, lum=0, contrast=0):
    """Adjusts the luminosity and contrast of a frame."""
    # Formula: new_image = alpha * original_image + beta
    # alpha (contrast): >1.0 increases, <1.0 decreases
    # beta (brightness): positive increases, negative decreases
    alpha = 1.0 + (contrast / 127.0)
    beta = lum
    adjusted = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
    return adjusted

def _apply_blur(frame, ksize=(5, 5)):
    """Applies a standard box blur."""
    # ksize must be a tuple of odd numbers
    ksize = (int(ksize[0]) // 2 * 2 + 1, int(ksize[1]) // 2 * 2 + 1)
    return cv2.blur(frame, ksize)

def _apply_gaussian_blur(frame, ksize=(5, 5), sigmaX=0):
    """Applies a Gaussian blur."""
    ksize = (int(ksize[0]) // 2 * 2 + 1, int(ksize[1]) // 2 * 2 + 1)
    return cv2.GaussianBlur(frame, ksize, sigmaX)

def _apply_median_blur(frame, ksize=5):
    """Applies a median blur, effective for removing noise."""
    # ksize must be an odd integer
    ksize = int(ksize) // 2 * 2 + 1
    return cv2.medianBlur(frame, ksize)

def _apply_color_tint(frame, color: str):
    """Applies a red, green, or blue tint to the frame."""
    b, g, r = cv2.split(frame)
    zeros = np.zeros_like(b)
    
    if color == 'red':
        # Boost red, suppress others slightly
        return cv2.merge([zeros, zeros, r])
    elif color == 'green':
        return cv2.merge([zeros, g, zeros])
    elif color == 'blue':
        return cv2.merge([b, zeros, zeros])
    else:
        return frame # Return original if color is not recognized


# --- Filter Dispatcher ---
# This map links the AI's filter names to our stable OpenCV functions.
CV2_FILTERS = {
    "blackwhite": _apply_blackwhite,
    "sepia": _apply_sepia,
    "lum_contrast": _adjust_lum_contrast,
    "blur": _apply_blur,
    "gaussian_blur": _apply_gaussian_blur,
    "median_blur": _apply_median_blur,
    "color_tint": _apply_color_tint,
}

def apply_effects(clip: VideoClip, filter_name: str, **kwargs) -> VideoClip:
    """
    Applies a video effect using a stable backend, dispatching to either
    OpenCV for frame-by-frame filters or moviepy for time-based effects.
    """
    # --- Time-based effects (handled by moviepy) ---
    if filter_name == "fadein":
        kwargs.setdefault('duration', 3.0) # Set default duration to 3 seconds
        return clip.fadein(**kwargs)
    if filter_name == "fadeout":
        kwargs.setdefault('duration', 3.0) # Set default duration to 3 seconds
        return clip.fadeout(**kwargs)

    # --- Frame-by-frame effects (handled by OpenCV) ---
    if filter_name not in CV2_FILTERS:
        raise ValueError(f"Filter '{filter_name}' is not a supported effect.")

    filter_func = CV2_FILTERS[filter_name]

    # Use a lambda to pass keyword arguments to the filter function
    return clip.fl_image(lambda frame: filter_func(frame, **kwargs))


# --- Other Effects (Text Overlays) ---
# These can remain as they are, since they are stable.

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
