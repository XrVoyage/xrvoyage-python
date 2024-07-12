import os
import time
import torch
import torchaudio
import torchaudio.functional as F
import librosa
import numpy as np
from scipy.signal import butter, lfilter
from dotenv import load_dotenv
from logzero import logger, loglevel
import logzero
import sounddevice as sd
import soundfile as sf

# Load environment variables from .env file
load_dotenv()

# Set log level to DEBUG to show all messages
loglevel(logzero.DEBUG)

def butter_lowpass(cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_highpass(cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

def highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

def speed_up_audio(audio_data, fs, speed_rate=1.2, n_fft=1024):
    logger.debug(f"TIME-SPEED: Applying speed rate {speed_rate}")
    
    # Ensure audio_data is float32
    audio_data = audio_data.astype(np.float32)
    
    # Set STFT parameters
    hop_length = n_fft // 4
    
    # Compute STFT
    stft = librosa.stft(audio_data, n_fft=n_fft, hop_length=hop_length)
    
    # Time-stretch the STFT
    stretched_stft = librosa.phase_vocoder(stft, rate=speed_rate, hop_length=hop_length)
    
    # Inverse STFT
    stretched_audio = librosa.istft(stretched_stft, hop_length=hop_length)
    
    return stretched_audio

def reduce_noise(data, fs):
    logger.debug("NOISE-REDUCTION: Applying")
    # Basic noise reduction (for demonstration purposes)
    noise_est = torch.mean(data)
    data = data - noise_est
    return data

def adjust_volume(data, target_db=-20.0):
    logger.debug(f"VOLUME-ADJUSTMENT: Adjusting to target dB {target_db}")
    rms = np.sqrt(np.mean(data**2))
    rms_db = 20 * np.log10(rms)
    adjustment_db = target_db - rms_db
    adjustment_factor = 10**(adjustment_db / 20)
    return data * adjustment_factor

def add_reverb(data, sr, reverb_amount=0.5):
    logger.debug(f"REVERB: Applying reverb amount {reverb_amount}")
    # Create a simple IR for reverb effect
    ir_length = int(sr * reverb_amount)
    ir = np.zeros(ir_length)
    ir[0] = 1.0
    ir[-1] = 0.5
    # Convolve the audio with the IR
    reverb_data = np.convolve(data, ir, mode='full')[:len(data)]
    return reverb_data

def add_delay(data, sr, delay_time=0.5, decay=0.5):
    logger.debug(f"DELAY: Applying delay time {delay_time}s with decay {decay}")
    delay_samples = int(delay_time * sr)
    delayed_data = np.zeros_like(data)
    delayed_data[delay_samples:] = data[:-delay_samples] * decay
    return data + delayed_data

def play_audio(file, low_freq=None, high_freq=None, playback_speed=1.2, 
               apply_noise_reduction=True, apply_highpass=False, apply_lowpass=False, 
               apply_speed_adjustment=True, target_db=-20.0, apply_reverb=False, reverb_amount=0.5,
               apply_delay=False, delay_time=0.5, delay_decay=0.5, time_measurements=False, n_fft=1024):
    try:
        total_conversion_time = 0
        
        start_time = time.time()
        data, fs = sf.read(file, dtype='float32')
        read_time = time.time() - start_time
        total_conversion_time += read_time
        logger.debug(f"AUDIO-READ: {file} shape={data.shape}, sample rate={fs}")

        if apply_noise_reduction:
            start_time = time.time()
            data = reduce_noise(torch.tensor(data), fs).numpy()
            noise_reduction_time = time.time() - start_time
            total_conversion_time += noise_reduction_time
            if time_measurements:
                logger.debug(f"NOISE-REDUCTION: Process Duration: {int(noise_reduction_time * 1000)}ms")
        
        if apply_highpass and low_freq is not None:
            logger.debug(f"HIGH-PASS: Applying cutoff {low_freq} Hz")
            start_time = time.time()
            data = highpass_filter(data, low_freq, fs)
            highpass_time = time.time() - start_time
            total_conversion_time += highpass_time
            if time_measurements:
                logger.debug(f"HIGH-PASS: Process Duration: {int(highpass_time * 1000)}ms")
        
        if apply_lowpass and high_freq is not None:
            logger.debug(f"LOW-PASS: Applying cutoff {high_freq} Hz")
            start_time = time.time()
            data = lowpass_filter(data, high_freq, fs)
            lowpass_time = time.time() - start_time
            total_conversion_time += lowpass_time
            if time_measurements:
                logger.debug(f"LOW-PASS: Process Duration: {int(lowpass_time * 1000)}ms")
        
        if apply_speed_adjustment:
            logger.debug(f"TIME-STRETCH: Applying speed rate {playback_speed}")
            start_time = time.time()
            if len(data.shape) > 1:  # if stereo
                data = np.array([speed_up_audio(channel, fs, playback_speed, n_fft) for channel in data.T]).T
            else:
                data = speed_up_audio(data, fs, playback_speed, n_fft)
            speed_adjustment_time = time.time() - start_time
            total_conversion_time += speed_adjustment_time
            if time_measurements:
                logger.debug(f"TIME-STRETCH: Process Duration: {int(speed_adjustment_time * 1000)}ms")
        
        data = adjust_volume(data, target_db)

        if apply_delay:
            data = add_delay(data, fs, delay_time, delay_decay)

        if apply_reverb:
            data = add_reverb(data, fs, reverb_amount)

        if not np.issubdtype(data.dtype, np.float32):
            data = data.astype(np.float32)
        
        start_time = time.time()
        sd.play(data, fs)
        sd.wait()  # Wait until file is done playing
        playback_time = time.time() - start_time
        logger.info(f"PLAYBACK: Process Duration: {int(playback_time * 1000)}ms")

        logger.info(f"TOTAL CONVERSION TIME: {int(total_conversion_time * 1000)}ms")
        logger.info(f"TOTAL PLAYBACK TIME: {int(playback_time * 1000)}ms")
    except Exception as e:
        logger.exception(f"Exception occurred while playing audio: {str(e)}")

# Example usage with custom settings
play_audio(
    "output.wav",
    low_freq=300,              # Low frequency cutoff for high-pass filter
    high_freq=3000,            # High frequency cutoff for low-pass filter
    playback_speed=1,        # Speed rate
    apply_noise_reduction=False,  # Apply noise reduction
    apply_highpass=True,       # Apply high-pass filter
    apply_lowpass=True,        # Apply low-pass filter
    apply_speed_adjustment=True,  # Apply speed adjustment
    target_db=-20.0,           # Target volume level in dB
    apply_reverb=True,         # Apply reverb
    reverb_amount=0.5,         # Amount of reverb
    apply_delay=False,         # Apply delay
    delay_time=0.5,            # Delay time in seconds
    delay_decay=0.5,           # Delay decay factor
    time_measurements=True,    # Time measurements
    n_fft=1024                 # FFT size
)
