from xrvoyage.models.events import XRWebhookEvent, XRWebhookEventBatch
import os
import json

class XREventsTester:
    def __init__(self, xr):
        self.xr = xr
    
    # def send_event_xr_data(self):
    #     event = XRWebhookEvent(
    #         type="xr.data.wh1",
    #         args={
    #             "key1": "value1",
    #             "key2": "value2",
    #             "key3": "value3",
    #             "key4": "value4"
    #         },
    #         project_guid="A3689E3BAA2B40389099DC91BCE30DF8",
    #     )

    #     event_batch = XRWebhookEventBatch(
    #         **{'xr.data': [event]}
    #     )
        
    #     # Convert to JSON and print beautified output
    #     event_batch_json = event_batch.model_dump_json(indent=4, by_alias=True, exclude_unset=True)
    #     print(event_batch_json)
        
    #     return self.xr.events.post_event(event_batch)


    def send_event_xr_data(self):
        payload_str = '''
            {
                "source": "690D3FAD36C34FD3BB4A9AFC0F6EB659",
                "type": "xr.data.llm-choice-destination",
                "args": {
                    "choice": "choiceValue"
                },
                "client": {
                    "session": "j2nmiYcYeD65MdAhJkWHiBoCFxUQHXj286nA",
                    "timestamp_utc": "1716644903763"
                }
            }
        '''
        
        payload_dict = json.loads(payload_str)
        
        event = XRWebhookEvent(
            source=payload_dict["source"],
            type=payload_dict["type"],
            args=payload_dict["args"],
            client=payload_dict["client"]
        )

        event_json = event.model_dump_json(indent=4, by_alias=True, exclude_unset=True)
        print("EVENT XR DATA EGRESS:", event_json)

        return self.xr.events.post_event(event)


    def send_event_xr_rt_status_ship_crew(self):
        payload_str = '''
        {
            "xr.rt": [
                {
                    "type": "xr.rt.status.ship.crew",
                    "args": {}
                }

            ]
        }
        '''
        
        payload_dict = json.loads(payload_str)
        
        # event = XRWebhookEvent(
        #     # source=payload_dict["xr.rt"][0]["source"],
        #     type=payload_dict["type"],
        #     args=payload_dict["args"]
        #     # client=payload_dict["xr.rt"][0]["client"]
        # )

        # event = XRWebhookEvent(
        #     **payload_dict
        # )

        event_batch = XRWebhookEventBatch(
            **payload_dict
        )
        
        # Convert to JSON and print beautified output
        event_batch_json = event_batch.model_dump_json(indent=4, by_alias=True, exclude_unset=True)
        print(event_batch_json)

        
        # return self.xr.events.post_event(event_batch)
        return self.xr.events.post_event_as_batch(event_batch)