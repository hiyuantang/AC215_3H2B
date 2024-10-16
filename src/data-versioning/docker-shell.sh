#!/bin/bash

set -e

# Read the settings file
source ../env.dev

export REPO_DIR=$(cd "$BASE_DIR/../.." && pwd)
export IMAGE_NAME="data-versioning"


echo "Building image"
docker build -t $IMAGE_NAME -f Dockerfile .

echo "Running container"
docker run --rm --name $IMAGE_NAME -ti \
--privileged \
--cap-add SYS_ADMIN \
--device /dev/fuse \
-v "$REPO_DIR":/app \
-v "$SECRETS_DIR":/secrets \
-v ~/.gitconfig:/etc/gitconfig \
-e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
-e GCP_PROJECT=$GCP_PROJECT \
-e GCP_ZONE=$GCP_ZONE \
-e GCS_BUCKET_NAME=$GCS_BUCKET_NAME \
$IMAGE_NAME