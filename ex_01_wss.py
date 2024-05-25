import os
import asyncio
import json
import xrvoyage
from xrvoyage import XrApiClient
from xrvoyage.handlers.wss import WssHandler, eventIngress
from xrvoyage.models.events import XRWebhookEventBatch
from dotenv import load_dotenv

load_dotenv()

# Print XrVoyage version
print("XrVoyage Version: ", xrvoyage.__version__)

# Using credentials to obtain the token so it can be used for API calls
xr = XrApiClient()
ship_guid = "C9EECCC7826249E386B45B78D8A14B19"

@eventIngress("xr.data.wh1")
def handle_some_data(event: XRWebhookEventBatch):
    print("Handling event of type 'xr.data.wh1'")
    # Print the full JSON event prettified with indent 4
    event_json = json.dumps(event, indent=4)
    print("Event data:", event_json)

async def main():
    # Connect to the WebSocket and listen for events
    await xr.wss.connect(ship_guid)  # Await the async connect method
    
    # Call the function from ex_02_datahook.py to send the payload
    from ex_02_datahook import DataHookTester
    tester = DataHookTester(xr)
    response = tester.send_test_payload()
    print("DATA SEND PAYLOAD", response)

    try:
        # Run the event loop for a while to demonstrate
        await asyncio.sleep(30)  # Adjust the sleep time as needed for your testing
    finally:
        # Destroy the WebSocket connection when done
        await xr.wss.destroy()

if __name__ == "__main__":
    asyncio.run(main())
