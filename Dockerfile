# syntax=docker/dockerfile:1

FROM python:3-buster

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update && \
    apt-get install -y \
    libatlas3-base libgfortran5 \
    libjbig0 liblcms2-2 libopenjp2-7 libtiff5 libwebp6 libwebpdemux2 libwebpmux3

RUN pip install --upgrade pip --extra-index-url https://www.piwheels.org/simple
#RUN pip install --upgrade setuptools wheel
RUN pip install --extra-index-url https://www.piwheels.org/simple numpy Flask Pillow

WORKDIR $VIRTUAL_ENV

COPY image_processor_server.py .

EXPOSE 8000

CMD [ "python3", "image_processor_server.py"]
