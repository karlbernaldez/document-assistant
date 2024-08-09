import os
from typing import IO
from io import BytesIO
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import pygame

# Set your ElevenLabs API key here if it's not already set in the environment variables
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "sk_1d086a19c57fce24423f587488aadec05f481fa3373e15d6")
client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# Define the character limit for the text-to-speech input
CHARACTER_LIMIT = 200
EXCEEDING_TEXT = "The answer is too long to read completely. Here is the first part:"

def text_to_speech_stream(text: str) -> IO[bytes]:
    """
    Convert text to speech using ElevenLabs API and return an audio stream.
    
    Args:
        text (str): The text to convert to speech. Should not exceed CHARACTER_LIMIT characters.
    
    Returns:
        IO[bytes]: The audio stream containing the speech.
    """
    if len(text) > CHARACTER_LIMIT:
        text = f"{EXCEEDING_TEXT} {text[:CHARACTER_LIMIT]}"

    response = client.text_to_speech.convert(
        voice_id="pNInz6obpgDQGcFmaJgB",  # Adam pre-made voice
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_multilingual_v2",
        voice_settings=VoiceSettings(
            stability=1.0,
            similarity_boost=1.0,
            style=1.0,
            use_speaker_boost=True,
        ),
    )

    audio_stream = BytesIO()
    for chunk in response:
        if chunk:
            audio_stream.write(chunk)

    audio_stream.seek(0)
    return audio_stream

def play_audio_stream(audio_stream: IO[bytes]):
    """
    Play an audio stream.
    
    Args:
        audio_stream (IO[bytes]): The audio stream to play.
    """
    audio_stream.seek(0)
    audio_data = audio_stream.read()
    
    # Save the audio data to a temporary MP3 file
    temp_filename = "response.mp3"
    with open(temp_filename, "wb") as f:
        f.write(audio_data)

    # Initialize pygame mixer
    pygame.mixer.init()
    pygame.mixer.music.load(temp_filename)
    pygame.mixer.music.play()

    # Wait for the audio to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    # Stop the mixer and quit
    pygame.mixer.music.stop()
    pygame.mixer.quit()

    # Clean up the temporary file
    os.remove(temp_filename)
