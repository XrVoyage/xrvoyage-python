from xrvoyage.models.data import DataWebhookEvent
import os

class DataHookTester:
    def __init__(self, xr):
        self.xr = xr
        self.webhook_id = os.getenv('WEBHOOK_ID')
    
    def send_test_payload(self):
        payload = DataWebhookEvent(
            type="xr.data.wh1",
            args={
                "key1": "value1",
                "key2": "value2",
                "key3": "value3",
                "key4": "value4"
            },
            project_guid="A3689E3BAA2B40389099DC91BCE30DF8",
        )
        
        return self.xr.data.post_webhook(self.webhook_id, payload)
        
