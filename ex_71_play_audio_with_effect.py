import os
import time
import torch
import torchaudio
import librosa
import numpy as np
from scipy.signal import butter, lfilter
from dotenv import load_dotenv
import sounddevice as sd
import soundfile as sf
from logzero import logger, loglevel
import logzero

# Load environment variables from .env file
load_dotenv()

# Set log level to DEBUG to show all messages
loglevel(logzero.DEBUG)

class AudioPlayerLocal:
    def __init__(self):
        # Load configuration from environment variables
        self.low_freq = int(os.getenv("AUDIO_PLAYER_LOCAL_LOW_FREQ", 400))
        self.high_freq = int(os.getenv("AUDIO_PLAYER_LOCAL_HIGH_FREQ", 1800))
        self.playback_speed = float(os.getenv("AUDIO_PLAYER_LOCAL_PLAYBACK_SPEED", 1.2))
        self.apply_noise_reduction = os.getenv("AUDIO_PLAYER_LOCAL_APPLY_NOISE_REDUCTION", "True").lower() == "true"
        self.apply_highpass = os.getenv("AUDIO_PLAYER_LOCAL_APPLY_HIGHPASS", "False").lower() == "true"
        self.apply_lowpass = os.getenv("AUDIO_PLAYER_LOCAL_APPLY_LOWPASS", "False").lower() == "true"
        self.target_db = float(os.getenv("AUDIO_PLAYER_LOCAL_TARGET_DB", -20.0))
        self.apply_reverb = os.getenv("AUDIO_PLAYER_LOCAL_APPLY_REVERB", "False").lower() == "true"
        self.reverb_amount = float(os.getenv("AUDIO_PLAYER_LOCAL_REVERB_AMOUNT", 0.5))
        self.reverb_decay = float(os.getenv("AUDIO_PLAYER_LOCAL_REVERB_DECAY", 0.5))
        self.reverb_mix = float(os.getenv("AUDIO_PLAYER_LOCAL_REVERB_MIX", 0.5))
        self.apply_delay = os.getenv("AUDIO_PLAYER_LOCAL_APPLY_DELAY", "False").lower() == "true"
        self.delay_time = float(os.getenv("AUDIO_PLAYER_LOCAL_DELAY_TIME", 0.5))
        self.delay_decay = float(os.getenv("AUDIO_PLAYER_LOCAL_DELAY_DECAY", 0.5))
        self.delay_mix = float(os.getenv("AUDIO_PLAYER_LOCAL_DELAY_MIX", 0.5))
        self.time_measurements = os.getenv("AUDIO_PLAYER_LOCAL_TIME_MEASUREMENTS", "False").lower() == "true"
        self.n_fft = int(os.getenv("AUDIO_PLAYER_LOCAL_N_FFT", 1024))

    def butter_lowpass(self, cutoff, fs, order=5):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a

    def butter_highpass(self, cutoff, fs, order=5):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='high', analog=False)
        return b, a

    def lowpass_filter(self, data, cutoff, fs, order=5):
        b, a = self.butter_lowpass(cutoff, fs, order=order)
        y = lfilter(b, a, data)
        return y

    def highpass_filter(self, data, cutoff, fs, order=5):
        b, a = self.butter_highpass(cutoff, fs, order=order)
        y = lfilter(b, a, data)
        return y

    def speed_up_audio(self, audio_data, fs, speed_rate=1.2, n_fft=1024):
        logger.debug(f"TIME-SPEED: Applying speed rate {speed_rate}")
        audio_data = audio_data.astype(np.float32)
        hop_length = n_fft // 4
        stft = librosa.stft(audio_data, n_fft=n_fft, hop_length=hop_length)
        stretched_stft = librosa.phase_vocoder(stft, rate=speed_rate, hop_length=hop_length)
        stretched_audio = librosa.istft(stretched_stft, hop_length=hop_length)
        return stretched_audio

    def reduce_noise(self, data, fs):
        logger.debug("NOISE-REDUCTION: Applying")
        noise_est = torch.mean(data)
        data = data - noise_est
        return data

    def adjust_volume(self, data, target_db=-20.0):
        logger.debug(f"VOLUME-ADJUSTMENT: Adjusting to target dB {target_db}")
        rms = np.sqrt(np.mean(data**2))
        rms_db = 20 * np.log10(rms)
        adjustment_db = target_db - rms_db
        adjustment_factor = 10**(adjustment_db / 20)
        return data * adjustment_factor

    def add_reverb(self, data, sr, reverb_amount=0.5, reverb_decay=0.5, reverb_mix=0.5):
        logger.debug(f"REVERB: Applying reverb amount {reverb_amount}, decay {reverb_decay}, mix {reverb_mix}")
        ir_length = int(sr * reverb_amount)
        ir = np.zeros(ir_length)
        ir[0] = 1.0
        ir[1:] = reverb_decay ** np.arange(1, ir_length)
        reverb_data = np.convolve(data, ir, mode='full')[:len(data)]
        return (1 - reverb_mix) * data + reverb_mix * reverb_data

    def add_delay(self, data, sr, delay_time=0.5, decay=0.5, delay_mix=0.5):
        logger.debug(f"DELAY: Applying delay time {delay_time}s with decay {decay} and mix {delay_mix}")
        delay_samples = int(delay_time * sr)
        delayed_data = np.zeros_like(data)
        delayed_data[delay_samples:] = data[:-delay_samples] * decay
        return (1 - delay_mix) * data + delay_mix * delayed_data

    def play_audio(self, file):
        try:
            total_conversion_time = 0
            start_time = time.time()
            data, fs = sf.read(file, dtype='float32')
            read_time = time.time() - start_time
            total_conversion_time += read_time
            logger.debug(f"AUDIO-READ: {file} shape={data.shape}, sample rate={fs}")

            if self.apply_noise_reduction:
                start_time = time.time()
                data = self.reduce_noise(torch.tensor(data), fs).numpy()
                noise_reduction_time = time.time() - start_time
                total_conversion_time += noise_reduction_time
                if self.time_measurements:
                    logger.debug(f"NOISE-REDUCTION: Process Duration: {int(noise_reduction_time * 1000)}ms")

            if self.apply_highpass and self.low_freq is not None:
                logger.debug(f"HIGH-PASS: Applying cutoff {self.low_freq} Hz")
                start_time = time.time()
                data = self.highpass_filter(data, self.low_freq, fs)
                highpass_time = time.time() - start_time
                total_conversion_time += highpass_time
                if self.time_measurements:
                    logger.debug(f"HIGH-PASS: Process Duration: {int(highpass_time * 1000)}ms")

            if self.apply_lowpass and self.high_freq is not None:
                logger.debug(f"LOW-PASS: Applying cutoff {self.high_freq} Hz")
                start_time = time.time()
                data = self.lowpass_filter(data, self.high_freq, fs)
                lowpass_time = time.time() - start_time
                total_conversion_time += lowpass_time
                if self.time_measurements:
                    logger.debug(f"LOW-PASS: Process Duration: {int(lowpass_time * 1000)}ms")

            if self.playback_speed != 1.0:
                logger.debug(f"TIME-STRETCH: Applying speed rate {self.playback_speed}")
                start_time = time.time()
                if len(data.shape) > 1:
                    data = np.array([self.speed_up_audio(channel, fs, self.playback_speed, self.n_fft) for channel in data.T]).T
                else:
                    data = self.speed_up_audio(data, fs, self.playback_speed, self.n_fft)
                speed_adjustment_time = time.time() - start_time
                total_conversion_time += speed_adjustment_time
                if self.time_measurements:
                    logger.debug(f"TIME-STRETCH: Process Duration: {int(speed_adjustment_time * 1000)}ms")

            data = self.adjust_volume(data, self.target_db)

            if self.apply_delay:
                data = self.add_delay(data, fs, self.delay_time, self.delay_decay, self.delay_mix)

            if self.apply_reverb:
                data = self.add_reverb(data, fs, self.reverb_amount, self.reverb_decay, self.reverb_mix)

            if not np.issubdtype(data.dtype, np.float32):
                data = data.astype(np.float32)

            start_time = time.time()
            sd.play(data, fs)
            sd.wait()
            playback_time = time.time() - start_time
            logger.info(f"PLAYBACK: Process Duration: {int(playback_time * 1000)}ms")

            logger.info(f"TOTAL CONVERSION TIME: {int(total_conversion_time * 1000)}ms")
            logger.info(f"TOTAL PLAYBACK TIME: {int(playback_time * 1000)}ms")
        except Exception as e:
            logger.exception(f"Exception occurred while playing audio: {str(e)}")

# Example usage
if __name__ == "__main__":
    player = AudioPlayerLocal()
    player.play_audio("output.wav")
