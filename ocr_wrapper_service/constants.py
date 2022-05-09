from configparser import ConfigParser
import os

filename = 'ocr_wrapper_service/config.ini'
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
    max_number_of_messages=10
    wait_time_seconds=20
    region = os.getenv("REGION")

class S3Constants():
    bucket_name=os.getenv("BUCKET_NAME")
    region=os.getenv("REGION")
    max_keys=10
    # model_path="IDM/model/ocr_model_psn_v1.0.0/model"
    model_path = "IDM/model/ocr_model_shrouds_v1.0.0/"
    model_count=3
    model_names=["^model_dotpunch_v.*.pth$","^model_prefix_v.*.pth$","^model_segmentation_v.*.pth$"]
    retry_sleep=300

class LocalDirectoryConstants():
    model_path=os.getenv('CONTAINER_MODEL_PATH')+"/model/"
    # # model_path="/models"
    # model_path = f"{config['S3']['MODEL_PATH']}{config['DEFAULT']['ACTIVE_RELEASE']}/"

class ModelDetails():
    active_release = config['DEFAULT']['ACTIVE_RELEASE']
    active_version = config[active_release]
    model_base_path =os.getenv('CONTAINER_MODEL_PATH')+"/model/"
    blade_config_base_path="ocr_analytic_service/componentBlade/"

    segmentation_config_path=blade_config_base_path + active_version['BLADE_SEG_CONFIG']
    segmentation_model_path= model_base_path  + active_version["BLADE_SEG_MODEL"]
    segmentation_threshold=float(active_version['BLADE_SEG_THRESHOLD'])
    
    
    dot_punch_config_path = blade_config_base_path + active_version['BLADE_PSN_CONFIG']
    dot_punch_model_path =  model_base_path  + active_version['BLADE_PSN_MODEL']
    dot_punch_threshold=float(active_version['BLADE_PSN_THRESHOLD'])
    
    prefix_config_path = blade_config_base_path + active_version['BLADE_PREFIX_CONFIG']
    prefix_model_path =  model_base_path  + active_version['BLADE_PREFIX_MODEL']
    prefix_threshold=float(active_version['BLADE_PREFIX_THRESHOLD'])
    
    dot_punch_pickle_path = blade_config_base_path + active_version['BLADE_PICKLE']

    shroud_config_base_path = "ocr_analytic_service/componentShroud/"
    
    shroud_seg_config_path = shroud_config_base_path + active_version['SHROUD_SEG_CONFIG']
    shroud_seg_model_path =  model_base_path  + active_version['SHROUD_SEG_MODEL']
    shroud_seg_threshold = float(active_version['SHROUD_SEG_THRESHOLD'])
    
    shroud_ocr_config_path = shroud_config_base_path + active_version['SHROUD_OCR_CONFIG']
    shroud_ocr_model_path =  model_base_path  + active_version['SHROUD_OCR_MODEL']
    shroud_ocr_threshold = float(active_version['SHROUD_OCR_THRESHOLD'])
    


