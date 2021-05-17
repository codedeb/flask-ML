from flask import Flask, request, jsonify
from .api_1_0.api import blueprint as api

def create_app(app_setting):
    app = Flask(__name__)
    app.config.from_object(app_setting)
    app.register_blueprint(api)
    return app
