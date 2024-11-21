#!/bin/bash

echo "Container is running!!!"

# Build the image
docker build -t api-service .

# Run tests
docker run -it --rm \
    -v "$(pwd):/app" \
    --entrypoint /bin/bash \
    api-service \
    -c "cd /app && PYTHONPATH=/app pipenv install --dev && PYTHONPATH=/app pipenv run pytest tests/ -v --cov=. --cov-report=xml"