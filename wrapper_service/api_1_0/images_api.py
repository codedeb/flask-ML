from flask_restplus import Resource, Namespace
from flask import jsonify, request
from wrapper_service.service.resize_image_service import resize_images

api = Namespace(name='image-ns', description='Image resize')


@api.route('/resize', methods=['POST'])
class SendMessages(Resource):
    @classmethod
    def post(cls):
        resize_images(request.data)
        return True

