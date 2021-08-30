from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor


def detector(config_path, model_weight_path, threshold):
    cfg = get_cfg()
    cfg.merge_from_file(config_path)
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = threshold  # set threshold for this model
    cfg.MODEL.DEVICE = "cpu"
    cfg.MODEL.WEIGHTS = model_weight_path
    predictor = DefaultPredictor(cfg)
    return predictor
