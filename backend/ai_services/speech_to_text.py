import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def transcribe_audio(audio_path: str) -> str:
    """
    Transcribes an audio file using OpenAI's Whisper model.

    Args:
        audio_path: The path to the audio file.

    Returns:
        The transcribed text.
    """
    with open(audio_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json" # Requesting timestamps
        )
    return transcription
