import os
class LoggerConstants():
    console_format="[%(levelname)s] - %(asctime)s - %(name)s - line number - %(lineno)d: %(message)s"
    date_format="%Y-%m-%d %H:%M:%S"

class FlaskConstants():
    host = "0.0.0.0"
    port = 8090
    cert_path="platform/ssl/ocrwrapper.crt"
    rsa_private_key_path="platform/ssl/ocrwrapper.key"
    debug=False

class SchedulerConstants():
    trigger="interval"
    seconds=1

class SQSConstants():
    input_queue="https://sqs.us-east-1.amazonaws.com/{}/{}".format(os.getenv('ACCOUNT_NUMBER'), os.getenv('INPUT_QUEUE'))
    output_queue="https://sqs.us-east-1.amazonaws.com/{}/{}".format(os.getenv('ACCOUNT_NUMBER'), os.getenv('OUTPUT_QUEUE'))
    max_number_of_messages=10
    wait_time_seconds=20

class S3Constants():
    bucket_name=os.getenv("BUCKET_NAME")
    max_keys=10
    model_path="IDM/model/ocr_model_psn_v1.0.0/model"

class LocalDirectoryConstants():
    model_path=os.getenv('MODEL_PATH')