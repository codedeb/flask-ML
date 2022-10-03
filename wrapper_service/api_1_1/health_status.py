from importlib.resources import contents
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Blueprint
import logging
from datetime import datetime
import requests
import os
import json
from pytz import utc
from requests.auth import HTTPBasicAuth



logger = logging.getLogger(__name__)

health_blueprint = Blueprint('health', __name__)

@health_blueprint.route('/api/status')
def healthy():
    status = {'status' : 'UP'}
    logger.info(f" OCR {status} @ {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    return status
    # status['OCR'] = 'UP'
    # try:
    #     bhoomi_url = 'https://boomi.power.ge.com/ws/rest/gegaspower/CPL/Parts/Nomination/PartsOut/parts-out-set-data/1358200'
    #     data = requests.get(bhoomi_url, auth=auth)
    #     if data.status_code == 200: 
    #         status['Boomi'] = 'UP'
    #     else:
    #         status['Boomi'] = 'DOWN'
    #     logger.info(f" health Status is {status} with status code {data.status_code} @ {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    # except:
    #     
    r
sched = BackgroundScheduler(timezone=utc,daemon=True)  
sched.add_job(healthy, 'interval', seconds=10)

sched.start()


          


