"""
Audio Diagnostic Script for VoicePilot.
Lists available input devices and checks live volume levels.
"""
import sounddevice as sd
import numpy as np

print("=== AVAILABLE AUDIO INPUT DEVICES ===")
devices = sd.query_devices()
default_input = sd.default.device[0]

for idx, dev in enumerate(devices):
    if dev['max_input_channels'] > 0:
        marker = " [DEFAULT]" if idx == default_input else ""
        print(f"Index {idx}: {dev['name']} (Channels: {dev['max_input_channels']}, Rate: {int(dev['default_samplerate'])}){marker}")

print("\n--- Testing 3-second recording on default device ---")
print("Speak into your microphone now...")

duration = 3  # seconds
sample_rate = 16000
recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
sd.wait()

max_amplitude = np.max(np.abs(recording))
mean_amplitude = np.mean(np.abs(recording))

print(f"\nMax volume detected:  {max_amplitude:.5f}")
print(f"Mean volume detected: {mean_amplitude:.5f}")

if max_amplitude < 0.01:
    print("\n[!] WARNING: Audio is essentially SILENT.")
    print("Likely causes: wrong device selected, hardware mute switch is on, or Windows input volume is at 0%.")
else:
    print("\n[OK] Microphone is capturing sound properly!")