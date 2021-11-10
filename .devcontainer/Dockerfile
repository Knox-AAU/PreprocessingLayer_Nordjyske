# Bases our image on Python 3.9
FROM python:3.9-slim-buster
RUN apt-get update

# Installs the dependencies located in the requirements.txt
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Ensures that Tesseract works, as well as a few other libraries
RUN apt-get update \
        && apt-get install -y \
        ffmpeg libsm6 libxext6  -y \
        build-essential \
        cmake \
        git \
        wget \
        tesseract-ocr \
    && apt-get update

# Sets the current work directory to the projectfolder
WORKDIR /preprocessinglayer_nordjysle

# Copies the training data
COPY ocr/trained_data_files /usr/share/tesseract-ocr/4.00/tessdata
