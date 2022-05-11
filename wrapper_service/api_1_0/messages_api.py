from flask_restplus import Resource, Namespace
# from wrapper_service.service.process_message_service import send_sqs_messages

api = Namespace(name='messages-ns', description='SQS Operations')

# @api.route('/send_messages', methods=['GET'])
# class SendMessages(Resource):
#     @classmethod
#     def get(cls):
#         result = send_sqs_messages()
#         return result

