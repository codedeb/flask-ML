from flask import Response
from flask import Blueprint

health_blueprint = Blueprint('health', __name__)

@health_blueprint.route('/api/status')
def health_status():
    result = {'status': 'UP'}
    return result