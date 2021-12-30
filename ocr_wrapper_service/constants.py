import os
class Logger_Constants():
    console_format="[%(levelname)s] - %(asctime)s - %(name)s - line number - %(lineno)d: %(message)s"
    date_format="%Y-%m-%d %H:%M:%S"

class Flask_Constants():
    host = "0.0.0.0"
    port = 8090
    cert_path="platform/ssl/ocrwrapper.crt"
    rsa_private_key_path="platform/ssl/ocrwrapper.key"
    debug=False

class Scheduler_Constants():
    trigger="interval"
    seconds=1

class SQS_Constants():
    input_queue="https://sqs.us-east-1.amazonaws.com/{}/{}".format(os.getenv('ACCOUNT_NUMBER'), os.getenv('INPUT_QUEUE'))
    output_queue="https://sqs.us-east-1.amazonaws.com/{}/{}".format(os.getenv('ACCOUNT_NUMBER'), os.getenv('OUTPUT_QUEUE'))
    max_number_of_messages=10
    wait_time_seconds=20

