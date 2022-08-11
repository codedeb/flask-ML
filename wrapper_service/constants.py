import os

from configparser import ConfigParser
filename = 'wrapper_service/config.ini'
config = ConfigParser()
config.read(filename)


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
    endpoint_url='https://sqs.us-east-1.amazonaws.com'
    # vpc_endpoint_url = 'https://vpce-0a1d31ed30e6eb61e-pvxlitlq.sqs.us-east-1.vpce.amazonaws.com'
    max_number_of_messages=10
    wait_time_seconds=20
    region = os.getenv("REGION")

class S3Constants():
    active_release = config['DEFAULT']['ACTIVE_RELEASE']
    active_version = config[active_release]
    bucket_name=os.getenv("BUCKET_NAME")
    region=os.getenv("REGION")
    max_keys=10
    model_path="IDM/model/v2.0.0/model"
    # model_path = f"{config['S3']['MODEL_PATH']}{config['DEFAULT']['ACTIVE_RELEASE']}"
    model_count=4
    model_names=["^model_segmentation_v.*.pth$","^model_shroud_segmentation_v.*.pth$","^model_shroud_OCR_v.*.pth$"]
    retry_sleep=300

class LocalDirectoryConstants():
    model_path=str(os.getenv('CONTAINER_MODEL_PATH'))+"/model/"
    #for local 
    # model_path="models/"

class ModelDetails():
    model_base_path=LocalDirectoryConstants.model_path
    #for local
    # model_base_path="models/"
    blade_config_base_path="analytic_service/componentBlade/"
   
    segmentation_config_path = blade_config_base_path+"config_segmentation_v1.1.0.yaml"
    segmentation_model_path = model_base_path+"model_segmentation_v1.1.0.pth"
    segmentation_threshold = 0.3
    dot_punch_config_path = blade_config_base_path + "config_shroud_OCR_v7.yaml"
    dot_punch_model_path = model_base_path + "model_shroud_OCR_v7.pth"
    dot_punch_threshold = 0.2

    shroud_config_base_path = "analytic_service/componentShroud/"
    shroud_seg_config_path = shroud_config_base_path + "config_shroud_segmentation_v3.yaml"
    shroud_seg_model_path = model_base_path + "model_shroud_segmentation_v3.pth"
    shroud_seg_threshold = 0.1
    shroud_ocr_config_path = shroud_config_base_path + "config_shroud_OCR_v7.yaml"
    shroud_ocr_model_path = model_base_path + "model_shroud_OCR_v7.pth"
    shroud_ocr_threshold = 0.3
    
    tp_cap_liner_config_base_path = "analytic_service/componentTpCapLiner/"
    tp_cap_liner_seg_config_path = tp_cap_liner_config_base_path + "config_LNCPTN_segmentation_v1.yaml"
    tp_cap_liner_seg_model_path = model_base_path + "model_LNCPTN_segmentation_v1.pth"
    tp_cap_liner_seg_threshold = 0.1
    tp_cap_liner_ocr_config_path = tp_cap_liner_config_base_path + "config_LNCPTN_OCR_v8.yaml"
    tp_cap_liner_ocr_model_path = model_base_path + "model_LNCPTN_OCR_v8.pth"
    tp_cap_liner_ocr_threshold = 0.1
    


