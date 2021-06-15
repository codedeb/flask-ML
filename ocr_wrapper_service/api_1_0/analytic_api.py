import json
from flask_restplus import Resource, Namespace
from flask import jsonify, request
from ocr_wrapper_service.service.analytic_service import process_images

api = Namespace(name='analytic-ns', description='Analytic Operations')


@api.route('/process_images', methods=['POST'])
class ProcessMessages(Resource):
    @classmethod
    def post(cls):
        print('data', request.data)
        result = process_images(request.data)
        return result

