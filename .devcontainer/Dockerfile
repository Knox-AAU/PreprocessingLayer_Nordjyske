# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.202.3/containers/python-3/.devcontainer/base.Dockerfile

# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT="3.9-bullseye"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# [Choice] Node.js version: none, lts/*, 16, 14, 12, 10
ARG NODE_VERSION="none"
RUN if [ "${NODE_VERSION}" != "none" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi

# Project requirements
RUN apt-get update
RUN python3.9 -m pip install pip

#Install the dependencies located in the requirements.txt
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Ensures that tesseract works, as well as a few other libraries
RUN apt-get update \
        && sudo apt-get install -y \
        ffmpeg libsm6 libxext6  -y \
        build-essential libssl-dev \
        cmake \
        git \
        wget \
        tesseract-ocr

# Sets the current work directory to the projectfolder
WORKDIR /nordjyske-preprocessing

# Copies the
COPY ocr/trained_data_files /usr/share/tesseract-ocr/4.00/tessdata



