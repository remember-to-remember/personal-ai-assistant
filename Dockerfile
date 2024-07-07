FROM --platform=linux/amd64 python:3.12-slim-bullseye

WORKDIR /app

COPY ./core .

COPY requirements.txt /app

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt && \