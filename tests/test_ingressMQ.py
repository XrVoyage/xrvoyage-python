import os
import time
from dotenv import load_dotenv
from logzero import logger, setup_logger
from xroai.agents_pi.providers.rabbitmq import run_event_loop, ingressMQ, egressMQ, auto_consume

load_dotenv()

@auto_consume
class TestIngress:
    @ingressMQ('queueA')
    def getFromA(self, payload):
        logger.info(f"Received payload from queueA: {payload}")
        self.inator(payload)

    @egressMQ('queueB')
    def sendToB(self, payload):
        logger.info(f"Sending payload to queueB: {payload}")  
        return payload

    def inator(self, payload):
        time.sleep(3)
        self.sendToB({'hello': 'from IN'})

    def start(self, message):
        self.sendToB({'hello': message})

if __name__ == "__main__":
    setup_logger(name="rabbitmq_logger", level="DEBUG")
    validator = TestIngress().start("from IN - Initial")
    run_event_loop()