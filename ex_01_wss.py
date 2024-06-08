import os
import asyncio
import json
import xrvoyage
from xrvoyage import XrApiClient
from xrvoyage.handlers.decorators import eventIngress
from dotenv import load_dotenv

load_dotenv()

# print("XRVOYAGE_ACCESS_KEY_ID", os.environ.get('XRVOYAGE_ACCESS_KEY_ID'))
# print("XRVOYAGE_SECRET_ACCESS_KEY", os.environ.get('XRVOYAGE_SECRET_ACCESS_KEY'))

# Print XrVoyage version
print("XrVoyage Version: ", xrvoyage.__version__)

# Using credentials to obtain the token so it can be used for API calls
xr = XrApiClient()
ship_guid = "878EBE0DA02A4B68991E96D034853F9E" # Cadu's Ship

@eventIngress([
    "xr.data.wh1", 
    "xr.data.llm-choice-source", 
    "xr.data.llm-choice-destination",         
    "xr.rt.status.ship.crew",
    "xr.rt.status.ship.geo",
    "xr.data.vr-quiz-data",
    "xr.data.vr-quiz-theme"
    ])
def handle_events(event: dict):
    event_type = event.get("type")
    print(f"Handling event of type '{event_type}'")
    event_json = json.dumps(event, indent=4)
    print("Event data:", event_json)

async def main():
    # Connect to the WebSocket and listen for events
    await xr.wss.connect(ship_guid)  # Await the async connect method
    
    # Call the function from ex_02_datahook.py to send the payload
    # from ex_02_datahook import DataHookTester
    # tester = DataHookTester(xr)
    # response = tester.send_test_payload()
    # print("DATA SEND PAYLOAD", response)

    # Call the function from ex_02_datahook.py to send the payload
    from ex_04_events import XREventsTester
    xrtester = XREventsTester(xr)
    # response = xrtester.send_event_xr_rt_status_ship_geo()
    # response = xrtester.send_event_xr_rt_status_ship_crew()
    # response = xrtester.send_event_xr_data_llm_source()
    # response = xrtester.send_event_xr_data_llm_destination()
    response = xrtester.send_event_xr_data_vr_quiz_data()
    # print("XREVENTS SEND PAYLOAD", response)

    try:
        # Run the event loop for a while to demonstrate
        await asyncio.sleep(90)  # Adjust the sleep time as needed for your testing
    finally:
        # Destroy the WebSocket connection when done
        await xr.wss.destroy()

if __name__ == "__main__":
    asyncio.run(main())
