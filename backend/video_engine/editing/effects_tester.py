import sys
from pathlib import Path
from moviepy.editor import VideoFileClip

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))

from backend.video_engine.editing.effects import apply_effects
from backend.tests.create_sample_video import create_sample_video

# Define the output directory
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "effects_tests"
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

def run_effects_tests():
    """
    Tests the apply_effects function in effects.py directly.
    """
    sample_video_path = create_sample_video()
    
    effects_to_test = {
        "blackwhite": {},
        "invert_colors": {},
        "fadein": {"duration": 2},
        "fadeout": {"duration": 2},
        "MultiplyColor": {"factor": [1, 0, 1]}, # Magenta tint
        "lum_contrast": {"lum": 5}, # Brighten
        "rotate": {"angle": 45}
    }
    
    print("\n--- Running Direct Effects Application Tests ---")
    
    for i, (effect_name, params) in enumerate(effects_to_test.items()):
        print(f"\n--- Testing Effect: '{effect_name}' ---")
        try:
            with VideoFileClip(sample_video_path) as clip:
                processed_clip = apply_effects(clip, effect_name, **params)
                
                output_path = OUTPUT_DIR / f"effect_{i+1}_{effect_name}.mp4"
                processed_clip.write_videofile(str(output_path), codec="libx264", fps=24)
                print(f"  ✅ Effect applied successfully. Saved to: {output_path}")

        except Exception as e:
            print(f"  ❌ Test failed for '{effect_name}': {e}")

if __name__ == "__main__":
    run_effects_tests()
