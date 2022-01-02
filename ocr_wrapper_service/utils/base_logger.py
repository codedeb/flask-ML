import logging
from logging import Formatter
from logging import Filter
from ocr_wrapper_service.constants import LoggerConstants

class SkipScheduleFilter(logging.Filter):
    def filter(self,record):
        return not record.msg.find("skipped: maximum number of running instances reached (1)")

def log_initializer_future(logger_name="App Logger"):
    #log_file_format = "[%(levelname)s] - %(asctime)s - %(name)s - : %(message)s in %(pathname)s:%(lineno)d"
    # Main logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        Formatter(fmt='%(asctime)s %(process)d,%(threadName)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s',
                  datefmt='%Y-%m-%d %H:%M:%S'))
    logger.addHandler(console_handler)
    return logger


def log_initializer():
    """
    Used for Initializing Console Logger with Formatting Parameters
    :return: logger object
    """
    #log_file_format = "[%(levelname)s] - %(asctime)s - %(name)s - : %(message)s in %(pathname)s:%(lineno)d"
    logger = logging.getLogger()
    console_format = LoggerConstants.console_format
    date_format = LoggerConstants.date_format
    formatter=logging.Formatter(console_format,date_format)
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger

