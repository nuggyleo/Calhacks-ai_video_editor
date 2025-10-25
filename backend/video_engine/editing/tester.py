import os
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip, TextClip
from clips import split_video, concatenate_videos
from effects import apply_filter, add_subtitle
from export import export_video
from audio import set_audio
from backend.ai_services.speech_to_text import transcribe_audio

def run_tests():
    """
    Runs a series of tests for the video editing functionalities,
    outputting a separate video for each test.
    """
    # Define paths
    uploads_dir = "uploads"
    outputs_dir = "outputs"
    sample_video_path = os.path.join(uploads_dir, "sample.mp4")
    sample_audio_path = os.path.join(uploads_dir, "sample.mp3")

    # Create outputs directory if it doesn't exist
    if not os.path.exists(outputs_dir):
        os.makedirs(outputs_dir)

    # --- Check if sample video exists ---
    if not os.path.exists(sample_video_path):
        print(f"ERROR: Sample video not found at '{sample_video_path}'")
        print("Please add a 'sample.mp4' to the 'uploads' directory to run the tests.")
        return

    print("--- Starting Video Editing Tests ---")

    # --- 1. Concatenate 00:00-00:03 and 00:20-00:23 ---
    try:
        print("\n1. Testing Concatenation...")
        clip1 = split_video(sample_video_path, 0, 3)
        clip2 = split_video(sample_video_path, 20, 23)
        output_path = os.path.join(outputs_dir, "test_1_concatenated.mp4")
        concatenate_videos([clip1, clip2], output_path)
        print(f"   Success! Video saved to {output_path}")
    except Exception as e:
        print(f"   ERROR during concatenation test: {e}")

    # --- 2. Make a filter for the whole video ---
    try:
        print("\n2. Testing Filter...")
        full_clip = VideoFileClip(sample_video_path)
        # Applying a color saturation filter to make the effect noticeable
        filtered_clip = apply_filter(full_clip, "colorx", factor=1.5)
        output_path = os.path.join(outputs_dir, "test_2_filtered.mp4")
        export_video(filtered_clip, output_path)
        print(f"   Success! Video saved to {output_path}")
        full_clip.close() # Close the clip to free up resources
    except Exception as e:
        print(f"   ERROR during filter test: {e}")

    # --- 3. Split at 00:05 and delete the rest (Trim) ---
    try:
        print("\n3. Testing Trim (Split)...")
        trimmed_clip = split_video(sample_video_path, 0, 5)
        output_path = os.path.join(outputs_dir, "test_3_trimmed.mp4")
        export_video(trimmed_clip, output_path)
        print(f"   Success! Video saved to {output_path}")
    except Exception as e:
        print(f"   ERROR during trim test: {e}")

    # --- 4. Add subtitles ---
    try:
        print("\n4. Testing Subtitles...")
        full_clip = VideoFileClip(sample_video_path)
        subtitled_clip = add_subtitle(
            full_clip,
            "This is a test subtitle!",
            start_time=1,
            duration=4,
            fontsize=36,
            color='yellow'
        )
        output_path = os.path.join(outputs_dir, "test_4_subtitled.mp4")
        export_video(subtitled_clip, output_path)
        print(f"   Success! Video saved to {output_path}")
        full_clip.close()
    except Exception as e:
        print(f"   ERROR during subtitle test: {e}")

    # --- 5. Replace audio ---
    try:
        print("\n5. Testing Set Audio...")
        if not os.path.exists(sample_audio_path):
            print(f"   WARNING: Sample audio not found at '{sample_audio_path}'. Skipping test.")
        else:
            full_clip = VideoFileClip(sample_video_path)
            clip_with_new_audio = set_audio(full_clip, sample_audio_path)
            output_path = os.path.join(outputs_dir, "test_5_new_audio.mp4")
            export_video(clip_with_new_audio, output_path)
            print(f"   Success! Video saved to {output_path}")
            full_clip.close()
    except Exception as e:
        print(f"   ERROR during set audio test: {e}")

    # --- 6. Auto-generate subtitles ---
    try:
        print("\n6. Testing Auto-Subtitle Generation...")
        # Step A: Extract audio from the video clip
        print("   - Extracting audio...")
        full_clip = VideoFileClip(sample_video_path)
        audio_output_path = os.path.join(outputs_dir, "temp_audio.mp3")
        full_clip.audio.write_audiofile(audio_output_path)

        # Step B: Transcribe the audio
        print("   - Transcribing audio with Whisper...")
        transcription_result = transcribe_audio(audio_output_path)

        # Step C: Create subtitle clips and overlay them
        print("   - Generating subtitle clips...")
        subtitle_clips = []
        for segment in transcription_result['segments']:
            start_time = segment['start']
            end_time = segment['end']
            text = segment['text']

            # Create a text clip for each segment
            text_clip = (
                TextClip(text, fontsize=36, color='white', bg_color='black')
                .set_position(('center', 'bottom'))
                .set_start(start_time)
                .set_duration(end_time - start_time)
            )
            subtitle_clips.append(text_clip)
        
        # Overlay subtitles onto the original video
        final_video = CompositeVideoClip([full_clip] + subtitle_clips)

        # Step D: Export the final video
        print("   - Exporting final video...")
        output_path = os.path.join(outputs_dir, "test_6_auto_subtitled.mp4")
        export_video(final_video, output_path)
        print(f"   Success! Video saved to {output_path}")

        # Clean up temporary audio file
        os.remove(audio_output_path)

    except Exception as e:
        print(f"   ERROR during auto-subtitle test: {e}")


    print("\n--- All Tests Completed! ---")
    print(f"Check the '{outputs_dir}' directory for the output videos.")


if __name__ == "__main__":
    run_tests()
