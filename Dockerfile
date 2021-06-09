# https://hub.docker.com/_/python
FROM python:3.7
WORKDIR /ocr-wrapper-service
COPY . ./
EXPOSE 5000

ENV HTTPS_PROXY "http://PITC-Zscaler-Americas-Alpharetta3pr.proxy.corporate.ge.com:80"
ENV HTTP_PROXY "http://PITC-Zscaler-Americas-Alpharetta3pr.proxy.corporate.ge.com:80"

RUN pip install -r requirements.txt
CMD ["python", "./wsgi.py"]

# $ docker --version
# $ docker build -t sample-cicd:v1 .
# $ docker run -p sample-cicd:v1