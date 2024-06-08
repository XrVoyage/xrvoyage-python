import functools
from typing import Callable, Dict, List, Union, Any
from logzero import logger
from xrvoyage.models.events import XRWebhookEventBatch
from xrvoyage.entities.webhooks_xrweb import Webhooks_XRWebHandler

class DecoratorsHandlers:
    def __init__(self, webhooks_xrweb: Webhooks_XRWebHandler, project_guid: str):
        self.webhooks_xrweb = webhooks_xrweb
        self.project_guid = project_guid

    def eventIngress(self, event_types: Union[str, List[str]]):
        if isinstance(event_types, str):
            event_types = [event_types]

        def decorator(func: Callable[[Any, dict], None]):
            @functools.wraps(func)
            def wrapper(instance, *args, **kwargs):
                return func(instance, *args, **kwargs)

            for event_type in event_types:
                logger.debug(f'Registering eventIngress handler for event type: {event_type}')
                DecoratorsHandlers.event_handlers[event_type] = wrapper
            return wrapper
        return decorator

    def eventEgress(self, event_type: str):
        def decorator(func: Callable[..., Any]):
            @functools.wraps(func)
            def wrapper(instance, *args, **kwargs):
                event_details = func(instance, *args, **kwargs)
                event_args = event_details.get('args', {})

                root_key = ".".join(event_type.split(".")[:2])
                payload_dict = {
                    root_key: [
                        {
                            "project_guid": self.project_guid,
                            "type": event_type,
                            "args": event_args
                        }
                    ]
                }

                event_batch = XRWebhookEventBatch(**payload_dict)
                event_json = event_batch.model_dump_json(indent=4, by_alias=True, exclude_unset=True)
                logger.debug(f"EVENT {root_key.upper()} EGRESS: {event_json}")
                self.webhooks_xrweb.post_event_as_batch(event_batch)

                return event_args
            logger.debug(f'Registering eventEgress handler for event type: {event_type}')
            return wrapper
        return decorator

    event_handlers: Dict[str, Callable[[dict], None]] = {}
