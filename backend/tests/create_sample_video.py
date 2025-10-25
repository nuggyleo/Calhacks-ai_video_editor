import sys
from pathlib import Path
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

# Define the user's sample video path
USER_SAMPLE_VIDEO_PATH = PROJECT_ROOT / "upload" / "sample.mp4"

# Define the assets directory for the generated video
ASSETS_DIR = PROJECT_ROOT / "backend" / "tests" / "assets"
ASSETS_DIR.mkdir(exist_ok=True, parents=True)
GENERATED_SAMPLE_VIDEO_PATH = ASSETS_DIR / "sample_video.mp4"

def create_sample_video():
    """
    Provides a sample video for testing.
    Uses the user's video if available, otherwise generates a simple one.
    """
    if USER_SAMPLE_VIDEO_PATH.exists():
        print(f"--- Using user's sample video: {USER_SAMPLE_VIDEO_PATH} ---")
        return str(USER_SAMPLE_VIDEO_PATH)
    
    if GENERATED_SAMPLE_VIDEO_PATH.exists():
        print(f"--- Using generated sample video: {GENERATED_SAMPLE_VIDEO_PATH} ---")
        return str(GENERATED_SAMPLE_VIDEO_PATH)

    print("--- No user video found. Creating a simple sample video for testing. ---")
    
    # Create a simple 10-second color clip
    main_clip = ColorClip(size=(1280, 720), color=(100, 150, 200), duration=10)
    
    # Create a text clip
    text_clip = TextClip("Sample Video for Filter Testing", fontsize=70, color='white')
    text_clip = text_clip.set_position('center').set_duration(10)
    
    # Composite the clips
    final_clip = CompositeVideoClip([main_clip, text_clip])
    
    # Write the file
    final_clip.write_videofile(str(GENERATED_SAMPLE_VIDEO_PATH), codec="libx264", fps=24)
    
    print(f"✅ Sample video created at: {GENERATED_SAMPLE_VIDEO_PATH}")
    return str(GENERATED_SAMPLE_VIDEO_PATH)

if __name__ == "__main__":
    create_sample_video()
