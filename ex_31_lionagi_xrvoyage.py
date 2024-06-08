# example_31_lionagi_xrvoyage.py
import os
import asyncio
import json
from xrvoyage import XrApiClient
from dotenv import load_dotenv
from logzero import logger

load_dotenv()
ship_guid = "878EBE0DA02A4B68991E96D034853F9E"
xrclient = XrApiClient(ship_guid)
logger.info("XrVoyage Version: %s", xrclient.version)

@xrclient.decorators.eventIngress(["xr.data.vr-quiz-theme"])
def event_ingress_vr_quiz_theme(event: dict):
    event_json = json.dumps(event, indent=4)
    logger.info(f"eventIngress type: '{event.get('type')}'")
    logger.info("eventIngress data: %s", event_json)

@xrclient.decorators.eventEgress("xr.data.vr-quiz-data")
def event_egress_vr_quiz_data():
    from ex_32_quizmock import mock_quiz_data_json
    return {
        "args": mock_quiz_data_json()
    }

asyncio.run(xrclient.connect())
