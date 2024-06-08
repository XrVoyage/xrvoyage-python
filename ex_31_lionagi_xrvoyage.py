import os
import asyncio
import json
from xrvoyage import XrApiClient
from dotenv import load_dotenv
import logzero
from logzero import logger
from ex_33_quiz_lionagi import create_vr_quiz_agent

logzero.loglevel(logzero.DEBUG)

load_dotenv()
ship_guid = "878EBE0DA02A4B68991E96D034853F9E"
xrclient = XrApiClient(ship_guid)
logger.info("XrVoyage Version: %s", xrclient.version)

@xrclient.decorators.eventIngress(["xr.data.vr-quiz-theme"])
async def event_ingress_vr_quiz_theme(event: dict):
    theme = event["args"]["data"]["response"]["theme"]
    logger.info("eventIngress args.data.response.theme: %s", theme)

    vr_quiz_lionagi = create_vr_quiz_agent(theme)
    vr_quiz_result = (await vr_quiz_lionagi.execute())[0]

    logger.debug(f"VR Quiz Lionagi output: {json.dumps(vr_quiz_result, indent=4)}")
    egress_response = await event_egress_vr_quiz_data(vr_quiz_result)  # Pass the first element of the result list

    # Handle the response
    if egress_response.get('message', '').lower() == 'success':
        logger.info("Event egress successfully processed")
    else:
        logger.error("Event egress failed with response: %s", egress_response)

@xrclient.decorators.eventEgress("xr.data.vr-quiz-data")
async def event_egress_vr_quiz_data(payload):
    return {
        "args": payload  # Ensure the key is retained in the args
    }

asyncio.run(xrclient.connect())
