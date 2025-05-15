import os
import requests
from app.core.config import DEEPGRAM_API_KEY

TRANSCRIPT_DIR = "transcripts"
os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

def transcribe_audio(audio_path: str, transcript_path: str) -> str:
    """
    Transcribe an audio file using Deepgram API and save the transcript to a file.
    
    Args:
        audio_path (str): Path to the input audio file (e.g., 'downloads/audio.mp3').
        transcript_path (str): Path to save the transcript (e.g., 'transcripts/user1_video.txt').
    
    Returns:
        str: Path to the saved transcript file.
    
    Raises:
        Exception: If transcription fails (e.g., file not found, API error, empty transcript).
    """
    try:
        if not os.path.exists(audio_path):
            raise Exception("Audio file not found")

        api_url = "https://api.deepgram.com/v1/listen"
        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "audio/mp3"
        }
        params = {
            "model": "nova-2",
            "punctuate": "true",
            "language": "en",
            "profanity_filter": "true",
            "utterances": "false"
        }

        with open(audio_path, "rb") as audio_file:
            response = requests.post(api_url, headers=headers, params=params, data=audio_file)

        if response.status_code != 200:
            raise Exception(f"Deepgram API failed: {response.status_code} - {response.text}")

        transcript = response.json().get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")
        if not transcript:
            raise Exception("No transcript generated")

        os.makedirs(os.path.dirname(transcript_path), exist_ok=True)
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(transcript)

        return transcript_path

    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")