
import pytest
from werkzeug.test import Client
import json
from flask import jsonify
from analytic_service.input_mod import read_input_and_form_output

#Functional test
def test_analytics_blades():
    data = [{"imageId":1,"partDataType":"PARTSERIALNUMBER","partType":"BLADES","positionNumber":2,"componentId":9,"componentName":"Comp1","imagePath": "IMG_0096.jpg"}]
    assert data[0]['partType'] == 'BLADES'
    assert data[0]['imagePath'] == "IMG_0096.jpg"
    
        
        
def test_analytics_shrouds():
    data = [{"imageId":1,"partDataType":"PARTSERIALNUMBER","partType":"SHROUDS","positionNumber":2,"componentId":9,"componentName":"Comp1","imagePath": "IMG_18_30_PSN.jpg"}]
    assert data[0]['partType'] == 'SHROUDS'
    assert data[0]['imagePath'] == "IMG_18_30_PSN.jpg"
        
        
def test_analytics_TPCapLiners():
    data = [{"imageId":1,"partDataType":"PARTSERIALNUMBER","partType":"SHROUDS","positionNumber":2,"componentId":9,"componentName":"Comp1","imagePath": "random.jpg"}]
    assert data[0]['imagePath'] == "random.jpg"

    

    
