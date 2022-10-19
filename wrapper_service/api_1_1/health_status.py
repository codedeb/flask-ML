from importlib.resources import contents
from urllib import response
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Blueprint
import logging
from datetime import datetime
from matplotlib.font_manager import json_load
import requests
import os
import json
from pytz import utc
from requests.auth import HTTPBasicAuth
# from wrapper_service.constants import BoomiConstants

from requests.exceptions import RequestException



logger = logging.getLogger(__name__)

healthy= Blueprint('healthy', __name__)

@healthy.route('/ocr/health/status')
def OCR_health():
    status = {'status' : 'UP'}
    logger.info(f" {status} @ {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
    return status
# sched = BackgroundScheduler(timezone=utc,daemon=True)  
# sched.add_job(OCR_health, 'interval', seconds=10)

# sched.start()

# @healthy.route('/boomi/health/status')
# def boomi_health():
#     result = {}
#     base_url = BoomiConstants.BOOMI_PARTS_OUT_SET_URL
#     # base_url = "https://boomi.power.ge.com/ws/rest/gegaspower/CPL/Parts/Nomination/PartsOut/parts-out-set-data/1358200"
#     try:
#         r = requests.get(base_url)
#         r.raise_for_status()
#     except requests.exceptions.HTTPError as errh:
#         logger.error(f"Http Error:{errh}")
#         result= {'status' : 'DOWN'}
#         return result
#     except requests.exceptions.ConnectionError as errc:
#         logger.error(f"Error Connecting:{errc}")
#         result= {'status' : 'DOWN'}
#         return result
#     except requests.exceptions.Timeout as errt:
#         logger.error(f"Timeout Error:{errt}")
#         result= {'status' : 'DOWN'}
#         return result
#     except requests.exceptions.RequestException as err:
#         logger.error(f"OOps: Something Else {err}")
#         result= {'status' : 'DOWN'}
#         return result
    
#     status_url = base_url + "1358200"
#     auth = HTTPBasicAuth(BoomiConstants.BOOMI_USERNAME, BoomiConstants.BOOMI_PASSWORD)
#     # auth = HTTPBasicAuth('CPL@gepowerandwater-S7O7S9.HRELEZ', '1e532910-9b92-4902-89b5-4dfedd0caac3')
#     response=requests.get(status_url, auth=auth)
#     response.raise_for_status()
    
#     data = json.loads(response.content)
    
#     if response.status_code==200 and len(data)>=1:  
#         result = {'Status' : 'UP'}
#     else:
#         result = {'message' : 'No data Available'} 
        
#     return result

       


