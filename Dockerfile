# https://hub.docker.com/_/python
FROM python:3.7
WORKDIR /ocr-wrapper-service
COPY . ./
EXPOSE 5000

RUN pip install -r requirements.txt
CMD ["python", "./wsgi.py"]

# $ docker --version
# $ docker build -t sample-cicd:v1 .
# $ docker run -p sample-cicd:v1