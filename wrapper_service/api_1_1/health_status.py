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
auth = HTTPBasicAuth('CPL@gepowerandwater-S7O7S9.HRELEZ', '1e532910-9b92-4902-89b5-4dfedd0caac3')
@health_blueprint.route('/api/status')
def healthy():
    try:
        bhoomi_url = 'https://boomi.power.ge.com/ws/rest/gegaspower/CPL/Parts/Nomination/PartsOut/parts-out-set-data/1358200'
        data = requests.get(bhoomi_url, auth=auth)
        if data.status_code == 200: 
            status = 'UP'
        else:
            status = 'DOWN'
        logger.info(f" OCR health Status is UP @ {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
        logger.info(f" Bhoomi health Status is {status} @ {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    except:
        status = 'DOWN'
    
    return status

sched = BackgroundScheduler(timezone=utc,daemon=True)  
sched.add_job(healthy, 'interval', seconds=10)

sched.start()


          


