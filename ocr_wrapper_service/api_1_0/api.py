from flask import Blueprint
from flask_restplus import Api, fields
from .messages_api import api as messages_ns

blueprint = Blueprint("api", __name__, url_prefix="")
api = Api(app=blueprint,
          title='Image Inference API',
          version='1.0',
          description='Sample IDM Service',
          doc='/'
          )
input_fields = api.model(name="input",
                         model={})

input_fields_res = api.inherit("input", input_fields)

api.add_namespace(messages_ns, path='/messages-ns')
# from .views import api
