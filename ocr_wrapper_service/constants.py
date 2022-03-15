import os
class LoggerConstants():
    console_format="[%(levelname)s] %(asctime)s %(filename)s:%(lineno)d %(message)s"
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
    region = os.getenv("REGION")

class S3Constants():
    bucket_name=os.getenv("BUCKET_NAME")
    region=os.getenv("REGION")
    max_keys=10
    model_path="IDM/model/ocr_model_psn_v1.0.0/model"
    model_count=3
    model_names=["^model_dotpunch_v.*.pth$","^model_prefix_v.*.pth$","^model_segmentation_v.*.pth$"]
    retry_sleep=300

class LocalDirectoryConstants():
    model_path=os.getenv('CONTAINER_MODEL_PATH')+"/model/"

class ModelDetails():
    blade_config_base_path="ocr_analytic_service/service/componentBlade"
    model_base_path = os.getenv('CONTAINER_MODEL_PATH')+"/model/"
    segmentation_config_path=blade_config_base_path+"configSeg.yaml"
    segmentation_model_path=model_base_path+"model_segmentation_v1.1.0.pth"
    segmentation_threshold=0.3
    dot_punch_pickle_path = blade_config_base_path + "listPickle"
    dot_punch_config_path = blade_config_base_path + "configDotPunchPSN.yaml"
    dot_punch_model_path = model_base_path + "model_dotpunch_v1.1.0.pth"
    dot_punch_threshold=0.8
    prefix_config_path = blade_config_base_path + "configPrefix.yaml"
    prefix_model_path = model_base_path + "model_prefix_v1.1.0.pth"
    prefix_threshold=0.1

    shroud_config_base_path = "ocr_analytic_service/service/componentShroud"
    prefix_config_path = shroud_config_base_path + "configShroud.yaml"
    prefix_model_path = model_base_path + "model_shroud_OCR_v1.pth"


