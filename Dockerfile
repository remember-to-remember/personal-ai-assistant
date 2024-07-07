FROM --platform=linux/amd64 python:3.12-slim-bullseye

WORKDIR /app

COPY ./backend/api .

COPY ./backend/requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
