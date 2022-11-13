from google.cloud import speech
import speech_recognition as rec


client = speech.SpeechClient.from_service_account_json('pc-ctrl-key.json')
user_input = rec.Recognizer()

with rec.Microphone() as source:
    print("sey")
    recorded = user_input.listen(source)
recorded_wav = rec.AudioData.get_wav_data(recorded)
audio = speech.RecognitionAudio(content=recorded_wav)

config = speech.RecognitionConfig(sample_rate_hertz=44100, enable_automatic_punctuation=True, language_code='en-US')

response = client.recognize(config=config, audio=audio)
print(response)
