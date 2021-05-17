import json
from flask_restplus import Resource, Namespace
from flask import jsonify, request
from ocr_wrapper_service.service.message_service import process_sqs_messages
from ocr_wrapper_service.service.message_service import send_sqs_messages
from ocr_wrapper_service.service.message_service import read_csv

api = Namespace(name='messages-ns', description='SQS Operations')


@api.route('/process_messages', methods=['GET'])
class GetSqsMessages(Resource):
    @classmethod
    def get(cls):
        result = process_sqs_messages()
        # return jsonify({'Hello': 'World!'})
        return result


@api.route('/insert_messages', methods=['GET'])
class SendSqsMessages(Resource):
    @classmethod
    def get(cls):
        result = send_sqs_messages()
        return result


@api.route('/read_csv', methods=['GET'])
class ReadCSV(Resource):
    @classmethod
    def get(cls):
        result = read_csv('297719_dot_punched_IMG_2022.JPG')
        return result
