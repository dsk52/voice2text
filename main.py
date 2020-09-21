import os
import tempfile
from datetime import datetime, timedelta, timezone
from logging import getLogger, StreamHandler, INFO

from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage
from google.cloud.speech import enums

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(INFO)
logger.setLevel(INFO)
logger.addHandler(handler)
logger.propagate = False

input_bucket_name = os.environ.get("INPUT_BUCKET_NAME")
output_bucket_name = os.environ.get("OUTPUT_BUCKET_NAME")

def transcribe(file_name):
    """
    Speech APIでStorageのファイルからテキスト化する
    """
    client = speech.SpeechClient()

    language_code = "ja-jP"
    sample_rate_hertz = 48000
    # encoding = enums.RecognitionConfig.AudioEncoding.WAV

    config = {
        "language_code": language_code,
        "sample_rate_hertz": sample_rate_hertz,
        # "encoding": encoding,
    }
    audio = {
        "uri": f"gs://{input_bucket_name}/{file_name}"
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

def upload(upload_file, datas):
    """
    一時ディレクトリ内にデータを作成後アップロード
    """
    with tempfile.TemporaryDirectory() as tempdir:
        upload_file_path = os.path.join(tempdir, upload_file)

        with open(upload_file_path, 'w', encoding="utf-8") as f:
            f.write("\n".join(datas))

        __uploadToBucket(upload_file_path, upload_file)

def __uploadToBucket(source_file, upload_file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(output_bucket_name)
    blob = bucket.blob(upload_file_name)

    blob.upload_from_filename(source_file)

def voice2text(event, context):
    """
    main handler
    """
    source_file_name = event['name']
    if source_file_name is None:
        raise Exception('file param is empty')

    JST = timezone(timedelta(hours=+9), 'JST')
    now = datetime.now(JST)
    timestamp = now.strftime('%Y%m%d_%H%M%S')

    dirname, basename = os.path.split(source_file_name)
    basename_without_ext, ext = basename.split('.', 1)
    upload_file = f"{basename_without_ext}.{timestamp}.txt"

    texts = transcribe(source_file_name)
    texts = formatToTextList(texts)
    logger.info(f"[Start] file uploaded to storage: {upload_file}")
    upload(upload_file, texts)

    logger.info(f"[End] file uploaded to storage: {upload_file}")

