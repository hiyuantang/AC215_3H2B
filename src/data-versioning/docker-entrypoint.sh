#!/bin/bash

echo "Container is running!!!"


gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS
mkdir -p /mnt/gcs_bucket
gcsfuse --key-file=$GOOGLE_APPLICATION_CREDENTIALS $GCS_BUCKET_NAME /mnt/gcs_data
echo 'GCS bucket mounted at /mnt/gcs_data'
mkdir -p /app/cheese_dataset
mount --bind /mnt/gcs_data/images /app/cheese_dataset

pipenv shell