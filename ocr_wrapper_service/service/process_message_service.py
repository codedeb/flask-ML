from ocr_wrapper_service.service.analytic_service import process_images
from ocr_wrapper_service.utils.sqs_sender import send_sqs_messages


def process_messages(input_dct):
    output = process_images(input_dct)
    print('output', output)
    send_sqs_messages(output)
    return output




