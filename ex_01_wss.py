import os
import asyncio
import json
import xrvoyage
from xrvoyage import XrApiClient
#from xrvoyage.handlers.decorators import eventIngress
from dotenv import load_dotenv

load_dotenv()

# print("XRVOYAGE_ACCESS_KEY_ID", os.environ.get('XRVOYAGE_ACCESS_KEY_ID'))
# print("XRVOYAGE_SECRET_ACCESS_KEY", os.environ.get('XRVOYAGE_SECRET_ACCESS_KEY'))

# Print XrVoyage version
print("XrVoyage Version: ", xrvoyage.__version__)

# Using credentials to obtain the token so it can be used for API calls
ship_guid = "C9EECCC7826249E386B45B78D8A14B19" # Peter's Ship
xrclient = XrApiClient(ship_guid)


    # "xr.data.wh1", 
    # "xr.data.ps001", 
    # "xr.data.llm-choice-source", 
    # "xr.data.llm-choice-destination",         
    # "xr.rt.status.ship.crew",
    # "xr.rt.status.ship.geo",
    # "xr.data.vr-quiz-data",
    # "xr.data.vr-quiz-theme"
@xrclient.decorators.eventIngress(["xr.data.ps001"])
def handle_events(event: dict):
    event_type = event.get("type")
    print(f"Handling event of type '{event_type}'")
    event_json = json.dumps(event, indent=4)
    print("Event data:", event_json)

async def main():
    # Connect to the WebSocket and listen for events
    await xrclient.connect()  # Await the async connect method
    
    # Call the function from ex_02_datahook.py to send the payload
    # from ex_02_datahook import DataHookTester
    # tester = DataHookTester(xr)
    # response = tester.send_test_payload()
    # print("DATA SEND PAYLOAD", response)

    # Call the function from ex_02_datahook.py to send the payload
    from ex_04_events import XREventsTester
    xrtester = XREventsTester(xrclient)
    # response = xrtester.send_event_xr_rt_status_ship_geo()
    # response = xrtester.send_event_xr_rt_status_ship_crew()
    # response = xrtester.send_event_xr_data_llm_source()
    # response = xrtester.send_event_xr_data_llm_destination()
    # response = xrtester.send_event_xr_data_vr_quiz_data()
    # print("XREVENTS SEND PAYLOAD", response)

    try:
        # Run the event loop for a while to demonstrate
        await asyncio.sleep(180)  # Adjust the sleep time as needed for your testing
    finally:
        # Destroy the WebSocket connection when done
        await xrclient.wss.destroy()

if __name__ == "__main__":
    asyncio.run(main())
