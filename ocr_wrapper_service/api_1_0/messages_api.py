from flask_restplus import Resource, Namespace
from ocr_wrapper_service.service.rabbitq_service import send_messages


api = Namespace(name='messages-ns', description='SQS Operations')

@api.route('/send_messages', methods=['GET'])
class SendMessages(Resource):
    @classmethod
    def get(cls):
        result = send_messages()
        return result

