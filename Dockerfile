# syntax=docker/dockerfile:1

FROM python:3.9-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY image_processor_server.py .

CMD [ "python3", "image_processor_server.py"]
