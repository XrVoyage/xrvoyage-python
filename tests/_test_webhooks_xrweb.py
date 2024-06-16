import os
import asyncio
import pytest
from dotenv import load_dotenv
from xrvoyage.handlers.api_client import XrApiClient
from xrvoyage.handlers.wss_handler import eventIngress, WssHandler
from xrvoyage.models.events import XRWebhookEventBatch
import logzero
from logzero import logger

load_dotenv()

@pytest.fixture
def setup_environment(monkeypatch):
    logger.debug('Setting up environment variables')
    monkeypatch.setenv('XRVOYAGE_ACCESS_KEY_ID', os.getenv('XRVOYAGE_ACCESS_KEY_ID'))
    monkeypatch.setenv('XRVOYAGE_SECRET_ACCESS_KEY', os.getenv('XRVOYAGE_SECRET_ACCESS_KEY'))

@eventIngress("xr.data.some-data-id2")
def handle_some_data(event: XRWebhookEventBatch):
    logger.debug(f"Handling event of type 'xr.data.some-data-id2'")
    print("Handling event of type 'xr.data.some-data-id2'")
    print("Event data:", event)

@pytest.mark.asyncio
@pytest.mark.dependency(name='websocket_test')
async def test_websocket_handler(setup_environment):
    logger.debug('Starting test_websocket_handler')
    xr = XrApiClient()
    ship_guid = "C9EECCC7826249E386B45B78D8A14B19"
    timeout = int(os.getenv('WEBSOCKET_TIMEOUT'))

    xr.wss.connect(ship_guid)

    try:
        logger.debug(f'Running event loop for {timeout} seconds')
        await asyncio.sleep(timeout)
    finally:
        logger.debug('Destroying websocket connection at the end of the test')
        await xr.wss.destroy()

# Simple test to ensure pytest recognition
def test_simple():
    assert 1 + 1 == 2
