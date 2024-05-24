from xrvoyage.models.data import DataWebhookEvent
import os

class DataHookTester:
    def __init__(self, xr):
        self.xr = xr
        self.webhook_id = os.getenv('WEBHOOK_ID')
    
    def send_test_payload(self):
        payload = DataWebhookEvent(
            type="xr.data.some-data-id2",
            args={
                "key1": "value1",
                "key2": "value2",
                "key3": "value3",
                "key4": "value4"
            },
            project_guid="C7138CAE3EF14008ADEC225F368F376A",
            sender_sub="example_sender_sub",  # Add appropriate value
            sender_username="example_sender_username"  # Add appropriate value
        )
        
        response = self.xr.data.post_webhook(self.webhook_id, payload)
        return response
