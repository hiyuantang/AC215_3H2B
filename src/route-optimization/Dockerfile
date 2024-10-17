FROM python:3.11-slim-buster
ENV PYENV_SHELL=/bin/bash

RUN set -ex; \
    for i in $(seq 1 8); do mkdir -p "/usr/share/man/man${i}"; done && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends build-essential git curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip

RUN useradd -ms /bin/bash app -d /home/app -u 1000 -p "$(openssl passwd -1 Passw0rd)" && \
    mkdir -p /app && \
    chown app:app /app

USER app
WORKDIR /app
ADD --chown=app:app requirements.txt /app/
# Using pip since it's more appropriate for more lightweight applications like this script
RUN pip install --no-cache-dir -r requirements.txt
ADD --chown=app:app . /app
RUN chmod +x /app/cli.py

ENTRYPOINT ["python", "cli.py"]
