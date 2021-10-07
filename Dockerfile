# Using base image as slim-buster as it is 114MB when uncompressed with latest Python releases and benefits of Debian Buster
FROM python:3.6-slim-buster

# ENV HTTPS_PROXY "http://PITC-Zscaler-Americas-Alpharetta3pr.proxy.corporate.ge.com:80"
# ENV HTTP_PROXY "http://PITC-Zscaler-Americas-Alpharetta3pr.proxy.corporate.ge.com:80"

# COPY config/80proxy /etc/apt/apt.conf.d/80proxy

RUN apt-get update -y \
    && apt-get clean \
    && apt-get autoremove

# python3 pip manager
RUN apt-get install -y python3-pip
RUN python3 -m pip install --upgrade pip

# gcc compiler and opencv prerequisites
RUN apt-get -y install nano git build-essential libglib2.0-0 libsm6 libxext6 libxrender-dev libgl1-mesa-glx

# Docker’s layer caching to skip reinstallation of dependencies if no change in requirements.txt
COPY requirements.txt /

# install all requirements
RUN pip3 install -r /requirements.txt

# Detectron2 prerequisites
RUN pip3 install torch==1.9.0+cu102 torchvision==0.10.0+cu102 --trusted-host=download.pytorch.org -f https://download.pytorch.org/whl/torch_stable.html
RUN pip3 install -U 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI'

# Detectron2 - CPU copy
# RUN python3 -m pip install detectron2==0.5+cpu --trusted-host=dl.fbaipublicfiles.com -f https://dl.fbaipublicfiles.com/detectron2/wheels/cpu/index.html
RUN git clone --depth 1 --branch v0.1 https://github.com/facebookresearch/detectron2.git
RUN ls
RUN pip3 install -U detectron2/.

# Copy the code from local to docker contanier
COPY . /ocr-wrapper-service
WORKDIR ocr-wrapper-service

EXPOSE 5000

ENV AWS_ACCESS_KEY_ID=None  \
    AWS_SECRET_ACCESS_KEY=None \
    REGION=us-east-1 \
    INPUT_QUEUE=uai3046767-cpl-dev-idm-input \
    OUTPUT_QUEUE=uai3046767-cpl-dev-idm-output \
    AWS_ACCOUNT_NUMBER=598619258634 \
    ACCOUNT_NUMBER=598619258634 \
    BUCKET_NAME=uai3046767-cpl-dev \
    NAS_PATH=/opt/shared/data/cpl/idm \
    MODEL_PATH=/opt/shared/data/cpl/idm

ENTRYPOINT ["python3", "/ocr-wrapper-service/wsgi.py"]
