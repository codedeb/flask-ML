from flask_restplus import Resource, Namespace

api = Namespace(name='api', description='SQS Operations')


@api.route('/status', methods=['GET'])
class Status(Resource):
    @classmethod
    def get(cls):
        result = {'status': 'UP'}
        return result

