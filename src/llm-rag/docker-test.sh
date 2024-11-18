#!/bin/bash

# Make the script executable
chmod +x docker-test.sh

# Content of docker-test.sh
docker compose run --rm llm-rag pipenv run pytest tests/ -v --cov=. --cov-report=term-missing


