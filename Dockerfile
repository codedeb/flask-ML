FROM ubuntu:18.04
RUN apt-get update && apt-get install tesseract-ocr -y \
    python3 \
    #python-setuptools \
    python3-pip \
    && apt-get clean \
    && apt-get autoremove
WORKDIR /ocr-wrapper-service
COPY . ./
RUN python3 -m pip install --upgrade pip
RUN apt install -y libgl1-mesa-glx
RUN pip3 install -r requirements.txt
EXPOSE 5000

ENV RABBITMQ_HOST_NAME=rabbitmq \
    RABBITMQ_HOST_PORT=5672 \
    RABBITMQ_USERNAME=idm_user \
    RABBITMQ_PASSWORD=idm@user \
    RABBITMQ_EXCHANGE=idm.exchange \
    RABBITMQ_INPUT_QUEUE=idm_ocr_input_queue \
    RABBITMQ_OUTPUT_QUEUE=idm_ocr_output_queue
ENV HTTPS_PROXY "http://PITC-Zscaler-Americas-Alpharetta3pr.proxy.corporate.ge.com:80"
ENV HTTP_PROXY "http://PITC-Zscaler-Americas-Alpharetta3pr.proxy.corporate.ge.com:80"

ENTRYPOINT ["python3", "wsgi.py"]

# $ docker --version
# $ docker build -t sample-cicd:v1 .
# $ docker run -p sample-cicd:v1
