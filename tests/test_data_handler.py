import json
import os
import pytest
from dotenv import load_dotenv
from xrvoyage.handlers.auth import TokenStrategy
from xrvoyage.models.data import DataWebhookEvent
from xrvoyage.handlers.data_handler import DataHandler

load_dotenv()

@pytest.fixture
def test_payload():
    return '''
    {
        "type": "xr.data.wh1",
        "project_guid": "A3689E3BAA2B40389099DC91BCE30DF8",
        "args": {
            "key1": "",
            "key2": "Hello World",
            "key3": "value3",
            "key4": "value4"
        }
    }
    '''

@pytest.fixture
def webhook_id():
    return os.getenv('WEBHOOK_ID')

def test_parse_payload(test_payload):
    data = json.loads(test_payload)
    event_type = data.get('type')
    project_guid = data.get('project_guid')
    args = data.get('args', {})

    assert event_type == "xr.data.wh1"
    assert project_guid == "A3689E3BAA2B40389099DC91BCE30DF8"
    assert args["key2"] == "Hello World"

@pytest.mark.dependency(depends=['websocket_test'])
def test_post_webhook(monkeypatch, test_payload, webhook_id):
    monkeypatch.setenv('XRVOYAGE_ACCESS_KEY_ID', os.getenv('XRVOYAGE_ACCESS_KEY_ID'))
    monkeypatch.setenv('XRVOYAGE_SECRET_ACCESS_KEY', os.getenv('XRVOYAGE_SECRET_ACCESS_KEY'))

    data = json.loads(test_payload)
    event_type = data.get('type')
    project_guid = data.get('project_guid')
    args = data.get('args', {})

    token_strategy = TokenStrategy()
    data_handler = DataHandler(token_strategy)
    webhook_event = DataWebhookEvent(type=event_type, project_guid=project_guid, args=args)

    # Mock the post_webook method to avoid making a real HTTP request
    def mock_post_webook(self, webhook_id, event):
        assert webhook_id == "6AstZDlkNGJV4XCzFHqCzsSEV79ayTcLS2ju87ViCTYKvUe99K3rSRa2eVUQfGyY"
        assert event.type == event_type
        assert event.project_guid == project_guid
        assert event.args["key2"] == "Hello World"

    monkeypatch.setattr(DataHandler, "post_webook", mock_post_webook)
    data_handler.post_webook(webhook_id, webhook_event)
