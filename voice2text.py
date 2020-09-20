import os
from google.cloud import speech_v1p1beta1
from google.cloud.speech_v1p1beta1 import enums

def transcribe(file_name):
    bucket_name = os.getenv("BUCKET_NAME")
    client = speech_v1p1beta1.SpeechClient()

    language_code = "ja-jP"
    sample_rate_hertz = 48000
    # encoding = enums.RecognitionConfig.AudioEncoding.WAV

    config = {
        "language_code": language_code,
        "sample_rate_hertz": sample_rate_hertz,
        # "encoding": encoding,
    }
    audio = {
        "uri": f"gs://{bucket_name}/{file_name}"
    }

    response = client.recognize(config, audio)

    for result in response.results:
        alternative = result.alternatives[0]
        print(u"Transcript: {}".format(alternative.transcript))


if __name__ == "__main__":
    transcribe('tagiri.wav')
