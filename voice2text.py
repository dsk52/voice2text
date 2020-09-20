import os
import datetime
from logging import getLogger, StreamHandler, INFO

from google.cloud import speech_v1p1beta1, storage
from google.cloud.speech_v1p1beta1 import enums

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(INFO)
logger.setLevel(INFO)
logger.addHandler(handler)
logger.propagate = False

bucket_name = os.environ.get("BUCKET_NAME")

def transcribe(file_name):
    """
    Speech APIでStorageのファイルからテキスト化する
    """
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
    operation = client.long_running_recognize(config, audio)
    response = operation.result()

    return response.results

def formatToTextList(datas):
    results = list()
    for result in datas:
        alternative = result.alternatives[0]
        results.append(f"{alternative.transcript}")

    return results

def writeText(upload_file, datas):
    with open(upload_file, 'w', encoding="utf-8") as f:
        f.write("\n".join(datas))

def uploadToBucket(source_file, upload_file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(upload_file_name)

    blob.upload_from_filename(source_file)

if __name__ == "__main__":
    source_file_name = 'tagiri.wav'

    now = datetime.datetime.now()
    timestamp = now.strftime('%Y-%m-%d_%H_%M_%S')

    dirname, basename = os.path.split(source_file_name)
    basename_without_ext, ext = basename.split('.', 1)
    output_file = f"{basename_without_ext}.txt"

    texts = transcribe(source_file_name)
    texts = formatToTextList(texts)
    writeText(output_file, texts)

    upload_file = f"{basename_without_ext}.{timestamp}.txt"
    uploadToBucket(output_file, upload_file)

    logger.info(f"file uploaded to storage: {upload_file}")
