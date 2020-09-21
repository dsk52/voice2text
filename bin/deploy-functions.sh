#!/bin/sh

pipenv shell && \
pipenv lock -r > requirements.txt

echo "[Start] deploy speech script..."

gcloud functions deploy voice2text \
--region=$REGION \
--runtime python38 \
--trigger-resource $INPUT_BUCKET_NAME \
--trigger-event google.storage.object.finalize \
--set-env-vars INPUT_BUCKET_NAME=voice2text_voice,OUTPUT_BUCKET_NAME=voice2text_text

echo "[End] deploy speech script."
