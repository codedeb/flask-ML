import json
from flask_restplus import Resource, Namespace
from flask import jsonify, request
from wrapper_service.service.analytic_service import process_images
from wrapper_service.utils.image_processor import process_image

api = Namespace(name='analytic-ns', description='Analytic Operations')


@api.route('/process_images', methods=['POST'])
class ProcessMessages(Resource):
    @classmethod
    def post(cls):
        print('data', request.data)
        result = process_image(request.data)
        return result

