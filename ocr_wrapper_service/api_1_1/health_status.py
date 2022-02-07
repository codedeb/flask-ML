import json
from flask import jsonify, request
from flask import Response
#from ocr_wrapper_service.service.analytic_service import process_images

#api = Namespace(name='analytic-ns', description='Analytic Operations')

from flask import Blueprint, render_template

health_blueprint = Blueprint('health', __name__)

@health_blueprint.route('/api/status')
def health_status():
    result = {'status': 'UP'}
    return result

