FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /opt/workspace

RUN apt-get update \
&& apt-get install gcc g++ -y \
&& apt-get clean

RUN pip3 install --upgrade pip

RUN pip3 install numpy --pre torch torchvision torchaudio --force-reinstall --index-url https://download.pytorch.org/whl/nightly/cpu
RUN pip3 install fairseq
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt --no-cache-dir

RUN apt-get install -y git wget unzip

ENV TZ Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY ./src ./src
COPY ./install_laser.sh ./install_laser.sh
RUN bash install_laser.sh
ENV PYTHONPATH="${PYTHONPATH}:/opt/workspace/src/laser/source"
ENV LASER=/opt/workspace/src/laser

COPY ./tmx_preprocessing.py ./tmx_preprocessing.py
COPY ./laser_cleaner.py ./laser_cleaner.py