# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster

WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-numpy \
    python3-pil \
    python3-flask

COPY image_processor_server.py .

CMD [ "python3", "image_processor_server.py"]
