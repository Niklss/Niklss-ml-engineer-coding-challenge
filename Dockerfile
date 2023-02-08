FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /opt/workspace

RUN apt-get update \
&& apt-get install gcc -y \
&& apt-get clean

RUN pip3 install --upgrade pip

RUN pip3 install torch
RUN pip3 install fairseq
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt --no-cache-dir

ENV TZ Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY ./src ./src
RUN export LASER=$PWD/src/laser
RUN bash src/laser/install_models.sh
RUN bash src/laser/install_external_tools.sh

COPY ./tmx_preprocessing.py ./tmx_preprocessing.py
COPY ./laser_cleaner.py ./laser_cleaner.py
