from flask import Flask, request
from wrapper_service.api_1_1.health_status import health_blueprint
from wrapper_service.api_1_0.api import blueprint
from flask_wtf.csrf import CSRFProtect


csrf = CSRFProtect()

def create_flask_app():
    """
    Creation of Flask API with only health status check endpoint
    :return:
    """
    app = Flask(__name__)
    app.register_blueprint(blueprint)
    app.register_blueprint(health_blueprint)
    csrf.init_app(app)
    return app