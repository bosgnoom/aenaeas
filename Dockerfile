# syntax=docker/dockerfile:1

FROM python:3

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install --upgrade pip --extra-index-url https://www.piwheels.org/simple
RUN pip install --upgrade setuptools wheel
RUN pip install --extra-index-url https://www.piwheels.org/simple numpy Flask Pillow

COPY image_processor_server.py .

EXPOSE 8000

CMD [ "python3", "image_processor_server.py"]
