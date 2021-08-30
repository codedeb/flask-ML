from .model_artifacts import detector
from .inference_prefix import getPrefix


def prefix_data_parser(imgobj):
    config_path = "ocr_analytic_service/service/configPrefix_file.yaml"
    base_path = os.getenv("NAS_PATH")
    model_weight_path = os.path.join(base_path, "/model_final_prefix.pth")
    # model_weight_path = r"../shared-volume/model_final_prefix.pth"
    threshold = 0.1
    prediction = detector(
        config_path, model_weight_path, threshold)
    prefix_out = getPrefix(imgobj, prediction)
    return prefix_out
