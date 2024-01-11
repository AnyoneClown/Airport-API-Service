FROM python:3.11.5-slim
LABEL maintainer="dum.denya15@gmail.com"

ENV PYTHONUNBUFFERED 1

WORKDIR app/

RUN apt-get update && apt-get install -y gcc libpq-dev netcat-openbsd

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
