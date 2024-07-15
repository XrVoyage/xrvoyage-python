import torch
import torchaudio
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import pyaudio
import numpy as np
import time
import logzero
from logzero import logger

# Initialize the Wav2Vec2 processor and model
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-large-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h")

# Initialize PyAudio
pa = pyaudio.PyAudio()
input_device_name = "IN 7-8 (3- BEHRINGER WING-USB)"

# Debug flag
DEBUG = True

# Find the device index for the input device name
def find_device_index(pa, device_name):
    device_index = None
    for i in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(i)
        if device_name in info.get('name'):
            device_index = i
            break
    if device_index is None:
        raise ValueError(f"Input device '{device_name}' not found.")
    return device_index

input_device_index = find_device_index(pa, input_device_name)

def record_audio(duration=3):
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=1024,
        input_device_index=input_device_index
    )

    frames = []
    for _ in range(int(16000 / 1024 * duration)):
        data = stream.read(1024)
        frames.append(np.frombuffer(data, dtype=np.int16))

    stream.stop_stream()
    stream.close()

    audio = np.concatenate(frames).astype(np.float32)  # Ensure the data is in float32 format
    return audio

def transcribe_audio(audio):
    input_values = processor(audio, return_tensors="pt", sampling_rate=16000).input_values
    with torch.no_grad():
        logits = model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = processor.batch_decode(predicted_ids)[0]
    return transcription.lower()

def keyword_spotting(transcription, keyword="computer"):
    words = transcription.split()
    for word in words:
        if keyword in word:
            return True
    return False

def detect_wake_word():
    logger.info("Sleeping...")
    while True:
        audio = record_audio(duration=1)
        transcription = transcribe_audio(audio)
        if DEBUG:
            logger.debug(f"Transcription: {transcription}")
        if keyword_spotting(transcription):
            logger.info("AWAKE")
            time.sleep(3)
            logger.info("Sleeping...")

if __name__ == "__main__":
    detect_wake_word()
