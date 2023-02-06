FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /opt/workspace

RUN apt-get update -y
RUN pip3 install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt --no-cache-dir

ENV TZ Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY ./src ./src
COPY ./main.py ./main.py
