import speech_recognition as sr
from google.cloud import speech_v1p1beta1 as speech

def listen_for_activation_word(recognizer, mic, activation_word="hey assistant"):
    print(f"Listening for activation word '{activation_word}'...")
    while True:
        with mic as source:
            audio = recognizer.listen(source)
        try:
            transcription = recognizer.recognize_google(audio).lower()
            if activation_word in transcription:
                print("Activation word detected!")
                return
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

def transcribe_audio(mic_index):
    recognizer = sr.Recognizer()
    mic = sr.Microphone(device_index=mic_index)
    listen_for_activation_word(recognizer, mic)  # Listen for the activation word
    with mic as source:
        print("Say something:")
        audio = recognizer.listen(source)

    try:
        client = speech.SpeechClient()
        audio_data = sr.AudioData(audio.get_raw_data(), source.SAMPLE_RATE, source.SAMPLE_WIDTH)
        content = audio_data.get_wav_data()

        response = client.recognize(
            config=speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=source.SAMPLE_RATE,  # Match the sample rate of the microphone
                language_code="en-US",
            ),
            audio=speech.RecognitionAudio(content=content)
        )

        if response.results:
            transcript = response.results[0].alternatives[0].transcript
            print("You said: " + transcript)
            return transcript
        else:
            print("No speech detected.")
            return None
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
