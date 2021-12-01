# Bases our image on Python 3.9
FROM python:3.9-slim-buster

# Installs the dependencies located in the requirements.txt
COPY ./requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN apt-get update \
        && apt-get install -y \
        git \
        wget \
    && apt-get update

WORKDIR /PreprocessingLayer_Nordjyske