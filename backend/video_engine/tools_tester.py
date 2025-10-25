import sys
from pathlib import Path
from moviepy.editor import VideoFileClip

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

from backend.video_engine.tools import apply_filter_to_video, trim_video
from backend.tests.create_sample_video import create_sample_video

# Define the output directory
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "tools_tests"
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

def run_tools_tests():
    """
    Tests the tool functions in tools.py.
    """
    sample_video_path = create_sample_video()
    
    # --- Test apply_filter_to_video ---
    print("\n--- Testing apply_filter_to_video Tool ---")
    filter_descriptions = [
        "make it black and white",
        "add a sepia filter",
        "darken the video"
    ]
    for i, desc in enumerate(filter_descriptions):
        print(f"\n--- Testing filter: '{desc}' ---")
        try:
            output_path = apply_filter_to_video(sample_video_path, desc)
            print(f"  ✅ Filter tool executed successfully. Saved to: {output_path}")
        except Exception as e:
            print(f"  ❌ Test failed for filter '{desc}': {e}")

    # --- Test trim_video ---
    print("\n--- Testing trim_video Tool ---")
    try:
        output_path = trim_video(sample_video_path, start_time=2, end_time=5)
        print(f"  ✅ Trim tool executed successfully. Saved to: {output_path}")
    except Exception as e:
        print(f"  ❌ Test failed for trim: {e}")

if __name__ == "__main__":
    run_tools_tests()
