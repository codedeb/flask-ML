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
    
# class BoomiConstants():
#     BOOMI_BASE_URL= os.getenv("BOOMI_BASE_URL")
#     BOOMI_PARTS_IN_SET_URL= os.getenv("BOOMI_PARTS_IN_SET_URL")
#     BOOMI_PARTS_IN_CHILD_URL=os.getenv("BOOMI_PARTS_IN_CHILD_URL")
#     BOOMI_PARTS_OUT_SET_URL= os.getenv("BOOMI_PARTS_OUT_SET_URL")
#     BOOMI_PARTS_OUT_CHILD_URL=os.getenv("BOOMI_PARTS_OUT_CHILD_")
#     BOOMI_USERNAME= os.getenv("BOOMI_USERNAME")
#     BOOMI_PASSWORD=os.getenv("BOOMI_PASSWORD")

class S3Constants():
    active_release = config['DEFAULT']['ACTIVE_RELEASE']
    active_version = config[active_release]
    bucket_name=os.getenv("BUCKET_NAME")
    region=os.getenv("REGION")
    max_keys=10
    model_path="IDM/model/v2.0.2/model"
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
    
    seg_config_base_path="analytic_service/config/segmentation/"
    ocr_config_base_path="analytic_service/config/ocr/"
   
    blades_seg_config_path = seg_config_base_path+"seg_config_file_v9.yaml"
    blades_seg_model_path = model_base_path+"model_final_seg_v9.pth"
    blades_seg_threshold = 0.3
    
    blades_ocr_config_path = ocr_config_base_path + "OCR_config_file_v9.yaml"
    blades_ocr_model_path = model_base_path + "model_final_ocr_v9.pth"
    blades_ocr_threshold = 0.2

  
    shroud_seg_config_path = seg_config_base_path + "config_shroud_segmentation_v3.yaml"
    shroud_seg_model_path = model_base_path + "model_shroud_segmentation_v3.pth"
    shroud_seg_threshold = 0.1
    
    shroud_ocr_config_path = ocr_config_base_path + "OCR_config_file_v9.yaml"
    shroud_ocr_model_path = model_base_path + "model_final_ocr_v9.pth"
    shroud_ocr_threshold = 0.3
    
  
    tp_cap_liner_seg_config_path = seg_config_base_path + "config_LNCPTN_segmentation_v1.yaml"
    tp_cap_liner_seg_model_path = model_base_path + "model_LNCPTN_segmentation_v1.pth"
    tp_cap_liner_seg_threshold = 0.1
    
    tp_cap_liner_ocr_config_path = ocr_config_base_path + "OCR_config_file_v9.yaml"
    tp_cap_liner_ocr_model_path = model_base_path + "model_final_ocr_v9.pth"
    tp_cap_liner_ocr_threshold = 0.1
    
    fuel_nozzles_seg_config_path = seg_config_base_path + "config_file.yaml"
    fuel_nozzles_seg_model_path = model_base_path + "model_final_fn_seg.pth"
    fuel_nozzles_seg_threshold = 0.1
    
    fuel_nozzles_ocr_config_path = ocr_config_base_path + "config_file.yaml"
    fuel_nozzles_ocr_model_path = model_base_path + "model_final_fn_ocr.pth"
    fuel_nozzles_ocr_threshold = 0.4
    


