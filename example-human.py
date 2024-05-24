import os
import asyncio
import xrvoyage
from xrvoyage import XrApiClient
from xrvoyage.handlers.wss import WssHandler, eventIngress
from xrvoyage.models.events import XRWebhookEventBatch
from dotenv import load_dotenv

load_dotenv()

print("XRVOYAGE_ACCESS_KEY_ID", os.environ.get('XRVOYAGE_ACCESS_KEY_ID'))
print("XRVOYAGE_SECRET_ACCESS_KEY", os.environ.get('XRVOYAGE_SECRET_ACCESS_KEY'))

# Print XrVoyage version
print("XrVoyage Version: ", xrvoyage.__version__)

# Using credentials to obtain the token so it can be used for API calls
xr = XrApiClient()
ship_guid = "C9EECCC7826249E386B45B78D8A14B19"

@eventIngress("xr.data.some-data-id2")
def handle_some_data(event: XRWebhookEventBatch):
    print("Handling event of type 'xr.data.some-data-id2'")
    print("Event data:", event)

async def main():
    # Connect to the WebSocket and listen for events
    xr.wss.connect(ship_guid)
    print ("not holding")

    try:
        # Run the event loop for a while to demonstrate
        await asyncio.sleep(30)  # Adjust the sleep time as needed for your testing
    finally:
        # Destroy the WebSocket connection when done
        await xr.wss.destroy()



if __name__ == "__main__":
    asyncio.run(main())
