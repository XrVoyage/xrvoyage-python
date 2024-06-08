import functools
import asyncio
import json
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
            async def async_wrapper(*args, **kwargs):
                try:
                    await func(*args, **kwargs)
                except KeyError as e:
                    logger.error(f"KeyError accessing event data: {e}")
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decoding error: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error: {e}", exc_info=True)
                    raise e  # Re-raise the exception to propagate it if necessary

            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except KeyError as e:
                    logger.error(f"KeyError accessing event data: {e}")
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decoding error: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error: {e}", exc_info=True)
                    raise e  # Re-raise the exception to propagate it if necessary

            for event_type in event_types:
                logger.debug(f'Registering eventIngress handler for event type: {event_type}')
                if asyncio.iscoroutinefunction(func):
                    DecoratorsHandlers.event_handlers[event_type] = async_wrapper
                else:
                    DecoratorsHandlers.event_handlers[event_type] = wrapper
            return func
        return decorator

    def eventEgress(self, event_type: str):
        def decorator(func: Callable[..., Any]):
            @functools.wraps(func)
            async def async_wrapper(instance, *args, **kwargs):
                try:
                    event_details = await func(instance, *args, **kwargs)
                    event_args = event_details.get('args', {})

                    payload_dict = {
                        "xr.data": [
                            {
                                "project_guid": self.project_guid,
                                "type": event_type,
                                "args": event_args  # Ensure args contains the full dictionary with xrvoyage_game key
                            }
                        ]
                    }

                    event_batch = XRWebhookEventBatch(**payload_dict)
                    event_json = event_batch.model_dump_json(indent=4, by_alias=True, exclude_unset=True)
                    logger.debug(f"EVENT XR.DATA EGRESS: {event_json}")
                    response = await asyncio.get_event_loop().run_in_executor(None, self.webhooks_xrweb.post_event_as_batch, event_batch)

                    # Log the response
                    logger.debug(f"Egress response: {response}")
                    if isinstance(response, dict):
                        if response.get('message', '').lower() == 'success':
                            logger.info("Event egress successfully processed")
                        else:
                            logger.error("Event egress failed with response: %s", response)
                    else:
                        logger.error(f"Unexpected response format: {response}")

                    return response

                except KeyError as e:
                    logger.error(f"KeyError accessing event data: {e}")
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decoding error: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error: {e}", exc_info=True)
                    raise e  # Re-raise the exception to propagate it if necessary

            return async_wrapper
        return decorator

    event_handlers: Dict[str, Callable[[dict], None]] = {}
