import os
import time
from dotenv import load_dotenv
from logzero import logger, setup_logger
from xroai.agents_pi.providers.rabbitmq import run_event_loop, ingressMQ, egressMQ, auto_consume
from xroai.agents_pi.tests.test_audio_sequences import TestAudioSequences

load_dotenv()

class EgressMQTest:
    # @egressMQ('control_player_local')
    # def send_to_control_player_local(self):
    #     logger.info(f"Sending payload to control_player_local")
    #     return TestAudioSequences().ve3ptv_test_with_sequence()


    # @egressMQ('control_agent_librarian')
    # def send_to_control_agent_librarian(self):
    #     logger.info(f"Sending payload to control_agent_librarian")
    #     return TestAudioSequences().ve3ptv_test_no_sequence()
    
    @egressMQ('control_agent_librarian')
    def send_to_control_agent_librarian(self):
        logger.info(f"Sending payload to control_agent_librarian")
        return TestAudioSequences().test_invalid_callsign()    



if __name__ == "__main__":
    setup_logger(name="control_player_logger", level="DEBUG")
    test = EgressMQTest()
    #while True:
        #test.send_to_control_player_local()
    test.send_to_control_agent_librarian()        
        #time.sleep(9)
    
