from flask import Flask, request
from api_1_1.health_status import health_blueprint

def create_flask_app():
    """
    Creation of Flask API with only health status check endpoint
    :return:
    """
    app = Flask(__name__)
    # app.register_blueprint(index_blueprint)
    app.register_blueprint(health_blueprint)
    return app