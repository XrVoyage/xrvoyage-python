import os
import time
from dotenv import load_dotenv
from logzero import logger, setup_logger
from xroai.agents_pi.providers.rabbitmq import run_event_loop, ingressMQ, egressMQ, auto_consume

load_dotenv()

class Processor:
    @egressMQ('control_player_local')
    def sendToA(self, payload):
        logger.info(f"Sending payload to control_player_local: {payload}")
        return payload


#@auto_consume
class TestIngress:
    def test(self):
        p = Processor()       
        p.sendToA(
            {
                "callsign": "VE3PTV",
                "command": "Proceeding to Sector 4",
                "command_ack": "Agent Victor Echo Three Papa Tango Victor is proceeding to Sector 4. Acknowledged",
                "sequence": [
                    {
                        "path": "xroai/agents_pi/audio-premade/Ring3.wav",
                        "target_db": -20.0,
                        #"low_freq": 400,
                        #"high_freq": 600,
                    },
                    {
                        "transcript": "Agent Victor Echo Three Papa Tango Victor is proceeding to Sector 4. Acknowledged",
                        "path": "output.wav",
                        "low_freq": 600,
                        "high_freq": 2000,
                        "playback_speed": 1.5,
                        "apply_noise_reduction": True,
                        "apply_highpass": True,
                        "apply_lowpass": True,
                        "target_db": -18.0,
                        "apply_reverb": False,
                        "reverb_amount": 0.5,
                        "reverb_decay": 0.5,
                        "reverb_mix": 0.5,
                        "apply_delay": False,
                        "delay_time": 0.5,
                        "delay_decay": 0.5,
                        "delay_mix": 0.5,
                        "time_measurements": False,
                        "n_fft": 1024                                                                                                                                       
                    },
                    {
                        "path": "xroai/agents_pi/audio-premade/RadioGlitch1.wav",
                        "target_db": -30.0,
                        "low_freq": 400,
                        "high_freq": 1200,    
                        "apply_highpass": True,
                        "apply_lowpass": True,                                            
                    }
                ]
            }
            )
     
       

if __name__ == "__main__":
    setup_logger(name="rabbitmq_logger", level="DEBUG")
    validator = TestIngress().test()
    ##run_event_loop()