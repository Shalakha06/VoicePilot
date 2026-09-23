"""
Push-to-Talk Speech-to-Text for VoicePilot using Faster-Whisper.
Bypasses virtual sound cards (like DroidCam) and supports flexible talking duration.
"""
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel


def get_real_mic_device() -> int:
    """Finds physical microphone (Nirvana Crystl, Intel Array, etc.), avoiding DroidCam."""
    devices = sd.query_devices()
    priority_keywords = ["nirvana", "crystl", "intel", "realtek", "array", "headset"]
    exclude_keywords = ["droidcam", "virtual", "stereo mix", "mapper"]

    for idx, dev in enumerate(devices):
        name = dev["name"].lower()
        if dev["max_input_channels"] > 0 and not any(ex in name for ex in exclude_keywords):
            if any(pk in name for pk in priority_keywords):
                return idx

    for idx, dev in enumerate(devices):
        if dev["max_input_channels"] > 0 and not any(ex in dev["name"].lower() for ex in exclude_keywords):
            return idx

    return sd.default.device[0]


class SpeechToText:
    def __init__(self, model_size: str = "base.en"):
        print("[STT] Initializing Faster-Whisper (base.en)...")
        self.sample_rate = 16000
        self.device_index = get_real_mic_device()
        self.whisper = WhisperModel(model_size, device="cpu", compute_type="int8", cpu_threads=4)

    def record_until_enter(self) -> np.ndarray:
        """Records from mic until user hits Enter in terminal."""
        input("\n[MIC] Press ENTER to start speaking...")
        print("[MIC] Listening... (Press ENTER again when done speaking)")

        recorded_chunks = []
        is_recording = True

        def callback(indata, frames, time_info, status):
            if is_recording:
                recorded_chunks.append(indata.copy())

        stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32',
            device=self.device_index,
            callback=callback
        )

        with stream:
            input()
            is_recording = False

        if not recorded_chunks:
            return np.array([], dtype=np.float32)

        audio = np.concatenate(recorded_chunks, axis=0).flatten()

        # Gain normalization for maximum accuracy
        peak = float(np.max(np.abs(audio))) if audio.size > 0 else 0.0
        if peak > 0.0002:
            audio = audio * (0.70 / max(peak, 0.01))

        return audio

    def listen_and_transcribe(self) -> str:
        audio = self.record_until_enter()
        if audio.size == 0 or np.max(np.abs(audio)) < 0.0005:
            return ""

        print("[STT] Transcribing speech...")
        segments, _ = self.whisper.transcribe(
            audio,
            beam_size=5,
            best_of=5,
            temperature=0.0,
            language="en"
        )
        return " ".join([s.text for s in segments]).strip()