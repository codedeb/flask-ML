
import pytest
from werkzeug.test import Client
from wsgi import app
import json
from flask import jsonify
from analytic_service.input_mod import read_input_and_form_output

#endpoint test

def test_analytics_blades():
    url = 'https://0.0.0.0:8090/api/analytic-ns/process_images'
    client= app.test_client()
    data = list()
    response = client.post(url, data=json.dumps(data))
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    
    
def test_analytics_shrouds():
    url = 'https://0.0.0.0:8090/api/analytic-ns/process_images'
    client= app.test_client()
    data = list()
    response = client.post(url, data=json.dumps(data))
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    

    

    
