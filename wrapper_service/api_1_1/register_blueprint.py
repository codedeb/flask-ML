from flask import Flask, request
from wrapper_service.api_1_1.health_status import healthy

def create_flask_app():
    """
    Creation of Flask API with only health status check endpoint
    :return:
    """
    app = Flask(__name__)
    app.register_blueprint(healthy)
    return app