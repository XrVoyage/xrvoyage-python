import os
import time
from dotenv import load_dotenv
from logzero import logger, setup_logger
from xroai.agents_pi.providers.rabbitmq import run_event_loop, ingressMQ, egressMQ, auto_consume

load_dotenv()

class Processor:
    @egressMQ('control_player_validator')
    def sendToA(self):
        payload = {'transcription': ' VICTOR ECHO 3 PAPA TANGO VICTOR PROCEED TO SECTOR 4'}
        logger.info(f"Sending payload to control_player_validator: {payload}")
        return payload


#@auto_consume
class TestIngress:
    def test(self):
        p = Processor()
        p.sendToA()

if __name__ == "__main__":
    setup_logger(name="rabbitmq_logger", level="DEBUG")
    validator = TestIngress().test()
    ##run_event_loop()