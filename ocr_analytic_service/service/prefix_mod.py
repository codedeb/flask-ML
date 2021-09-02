from .model_artifacts import detector
from .inference_prefix import getPrefix


def prefix_data_parser(imgobj):
    logger.info('Prefix model input: %s' % imgobj)
    config_path = "ocr_analytic_service/service/configPrefix_file.yaml"
    # base_path = os.getenv("NAS_PATH")
    # model_weight_path = os.path.join(base_path, "/models/model_final_prefix.pth")
    model_weight_path = "/opt/shared/data/cpl/idm/models/model_final_prefix.pth"
    # model_weight_path = r"/shared-volume/model_final_prefix.pth"
    logger.info('Prefix model path: %s' % model_weight_path)
    threshold = 0.1
    prediction = detector(
        config_path, model_weight_path, threshold)
    logger.info('Prefix model path prediction: %s' % prediction)
    prefix_out = getPrefix(imgobj, prediction)
    logger.info('Prefix model output: %s' % prefix_out)
    return prefix_out
