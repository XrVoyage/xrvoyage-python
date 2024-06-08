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


    def send_event_xr_data_llm_source(self):
        payload_str = '''
        {
            "xr.data": [
                {
                    "project_guid": "A895570833F0429A98940C079555AE51",
                    "type": "xr.data.llm-choice-source",
                    "args": {
                        "message": "hi there, Rogeno"
                    }
                }
            ]
        }
        '''
        payload_dict = json.loads(payload_str)
        event_batch = XRWebhookEventBatch(**payload_dict)
        event_json = event_batch.model_dump_json(indent=4, by_alias=True, exclude_unset=True)
        print("EVENT XR DATA EGRESS:", event_json)
        return self.xr.events.post_event_as_batch(event_batch)
    
    def send_event_xr_data_llm_destination(self):
        payload_str = '''
        {
            "xr.data": [
                {
                    "project_guid": "A895570833F0429A98940C079555AE51",
                    "type": "xr.data.llm-choice-destination",
                    "args": {
                        "answer": "YES"
                    }
                }
            ]
        }
        '''
        payload_dict = json.loads(payload_str)
        event_batch = XRWebhookEventBatch(**payload_dict)
        event_json = event_batch.model_dump_json(indent=4, by_alias=True, exclude_unset=True)
        print("EVENT XR DATA EGRESS:", event_json)
        return self.xr.events.post_event_as_batch(event_batch)    


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
    

    def send_event_xr_rt_status_ship_geo(self):
        payload_str = '''
        {
            "xr.rt": [
                {
                    "type": "xr.rt.status.ship.geo",
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
    

    def send_event_xr_data_vr_quiz_data(self):
        payload_str = '''
        {
            "xr.data": [
                {
                    "project_guid": "A895570833F0429A98940C079555AE51",
                    "type": "xr.data.vr-quiz-data",
                    "args": {
                        "xrvoyage_game": {
                            "theme": "mickey mouse",
                            "scenes": [
                                {
                                    "question": "What is the significance of Mickey Mouse's first appearance?",
                                    "story": "In 1928, Walt Disney introduced the world to Mickey Mouse in the animated short film 'Steamboat Willie'. This marked the beginning of a cultural phenomenon. Mickey quickly became a beloved character, symbolizing joy and imagination. The film was groundbreaking for its synchronized sound and innovative animation techniques.",        
                                    "choices": [
                                        {
                                            "name": "First synchronized sound cartoon",
                                            "correct_answer": true
                                        },
                                        {
                                            "name": "First color cartoon",
                                            "correct_answer": false
                                        },
                                        {
                                            "name": "First animated feature film",
                                            "correct_answer": false
                                        },
                                        {
                                            "name": "First cartoon with a storyline",
                                            "correct_answer": true
                                        }
                                    ]
                                },
                                {
                                    "question": "How did Mickey Mouse's design evolve over the years?",
                                    "story": "Mickey Mouse's design has undergone several changes since his debut. Initially, he had a more rat-like appearance with a long nose and small eyes. Over the years, his design was softened to make him more appealing. His eyes became larger, his nose shorter, and his body rounder. These changes helped Mickey remain relevant and beloved by audiences of all ages.",
                                    "choices": [
                                        {
                                            "name": "Larger eyes",
                                            "correct_answer": true
                                        },
                                        {
                                            "name": "Longer nose",
                                            "correct_answer": false
                                        },
                                        {
                                            "name": "Rounder body",
                                            "correct_answer": true
                                        },
                                        {
                                            "name": "Smaller ears",
                                            "correct_answer": false
                                        }
                                    ]
                                },
                                {
                                    "question": "What role did Mickey Mouse play in the development of animation technology?",
                                    "story": "Mickey Mouse was at the forefront of several technological advancements in animation. 'Steamboat Willie' was one of the first cartoons to feature synchronized sound, which was a major breakthrough at the time. Later, Mickey starred in 'The Band Concert', the first Mickey Mouse cartoon in color. These innovations set new standards in the industry and paved the way for future developments.",
                                    "choices": [
                                        {
                                            "name": "Synchronized sound",
                                            "correct_answer": true
                                        },
                                        {
                                            "name": "First 3D animation",
                                            "correct_answer": false
                                        },
                                        {
                                            "name": "First color cartoon",
                                            "correct_answer": true
                                        },
                                        {
                                            "name": "First use of CGI",
                                            "correct_answer": false
                                        }
                                    ]
                                }
                            ],
                            "choices": 4
                        }
                    }
                }
            ]
        }





        '''
        payload_dict = json.loads(payload_str)
        event_batch = XRWebhookEventBatch(**payload_dict)
        event_json = event_batch.model_dump_json(indent=4, by_alias=True, exclude_unset=True)
        print("EVENT XR DATA EGRESS:", event_json)
        return self.xr.events.post_event_as_batch(event_batch)    