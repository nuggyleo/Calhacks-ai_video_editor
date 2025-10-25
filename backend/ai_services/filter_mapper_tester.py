import sys
from pathlib import Path
from moviepy.editor import VideoFileClip
from backend.video_engine.editing.effects import apply_effects
from backend.ai_services.filter_mapper import map_description_to_filter
from backend.tests.create_sample_video import create_sample_video

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

# Define the output directory for the test videos
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "filter_tests"
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

def run_tests():
    """
    Runs a comprehensive series of tests on the new filter mapper.
    """
    sample_video_path = create_sample_video()
    
    test_cases = [
        "make the video black and white",
        "invert the colors",
        "flip horizontally",
        "fade in for 2.5 seconds",
        "fade out for 1 second",
        "darken the video a bit",
        "add a red tint",
        "rotate by 90 degrees",
        "this should fail completely"
    ]
    
    print("\n--- Running Comprehensive Filter Application Tests ---")
    
    for i, test in enumerate(test_cases):
        print(f"\n--- Test Case {i+1}: '{test}' ---")
        try:
            filter_info = map_description_to_filter(test)
            filter_name = filter_info['filter_name']
            parameters = filter_info['parameters']
            print(f"  ✅ Mapped to '{filter_name}' with params {parameters}")

            with VideoFileClip(sample_video_path) as clip:
                processed_clip = apply_effects(clip, filter_name, **parameters)
                
                output_filename = f"test_{i+1}_{filter_name}.mp4"
                output_path = OUTPUT_DIR / output_filename
                processed_clip.write_videofile(str(output_path), codec="libx264", fps=24, logger=None)
                print(f"  ✅ Filter applied and video saved to: {output_path}")

        except ValueError as e:
            print(f"  ❌ Failed as expected for unsupported filters: {e}")

if __name__ == "__main__":
    run_tests()
