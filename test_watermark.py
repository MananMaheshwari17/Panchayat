import numpy as np
import subprocess
import io
from scipy.fft import fft

def inject_audio_watermark(audio_bytes: bytes) -> bytes:
    try:
        # Decode
        process = subprocess.Popen(
            ["ffmpeg", "-i", "pipe:0", "-f", "s16le", "-ac", "1", "-ar", "44100", "pipe:1"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate(input=audio_bytes)
        
        if process.returncode != 0:
            print(f"Decode failed: {stderr.decode()}")
            return audio_bytes

        pcm_data = np.frombuffer(stdout, dtype=np.int16).astype(np.float32)
        sample_rate = 44100
        duration_sec = len(pcm_data) / sample_rate
        frequency = 19000
        
        t = np.linspace(0, duration_sec, len(pcm_data), False)
        sine_wave = np.sin(frequency * 2 * np.pi * t)
        
        pcm_normalized = pcm_data / 32768.0
        watermarked_float = pcm_normalized + (sine_wave * 0.05)
        watermarked_pcm = (np.clip(watermarked_float, -1.0, 1.0) * 32767).astype(np.int16)

        # Encode (to WAV for easier processing in test)
        process = subprocess.Popen(
            ["ffmpeg", "-f", "s16le", "-ac", "1", "-ar", "44100", "-i", "pipe:0", "-f", "wav", "pipe:1"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        final_audio, stderr = process.communicate(input=watermarked_pcm.tobytes())
        
        return final_audio
    except Exception as e:
        print(f"Injection Error: {e}")
        return audio_bytes

def has_valid_watermark(audio_bytes: bytes) -> bool:
    try:
        process = subprocess.Popen(
            ["ffmpeg", "-i", "pipe:0", "-f", "s16le", "-ac", "1", "-ar", "44100", "pipe:1"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate(input=audio_bytes)
        if process.returncode != 0:
            return False

        samples = np.frombuffer(stdout, dtype=np.int16)
        if len(samples) < 4096:
            return False
        
        start_idx = len(samples) // 4
        end_idx = 3 * len(samples) // 4
        sample_slice = samples[start_idx:end_idx]
        
        n = len(sample_slice)
        yf = fft(sample_slice)
        xf = np.fft.fftfreq(n, 1 / 44100)
        
        idx = np.where((xf > 18900) & (xf < 19100))
        magnitude = np.abs(yf[idx])
        
        if len(magnitude) == 0:
            return False
            
        peak_val = np.max(magnitude)
        print(f"Peak at 19kHz: {peak_val}")
        return peak_val > 500 # Slightly lower threshold for compressed audio
    except Exception as e:
        print(f"Verification Error: {e}")
        return False

# Generate 1 sec of silence (WAV)
process = subprocess.Popen(
    ["ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "1", "-f", "wav", "pipe:1"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
original_bytes, _ = process.communicate()

print("Testing watermark injection...")
watermarked_bytes = inject_audio_watermark(original_bytes)

print("Verifying original (should be False):")
print(has_valid_watermark(original_bytes))

print("Verifying watermarked (should be True):")
print(has_valid_watermark(watermarked_bytes))
