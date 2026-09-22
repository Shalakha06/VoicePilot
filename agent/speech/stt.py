"""
Speech-to-Text Module for VoicePilot.
Captures microphone audio and transcribes it locally using faster-whisper.
"""
import threading
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from agent.config import (
    STT_MODEL_SIZE,
    STT_DEVICE,
    STT_COMPUTE_TYPE,
    AUDIO_SAMPLE_RATE,
    AUDIO_INPUT_DEVICE
)


class SpeechToText:
    def __init__(self):
        print(f"[STT] Initializing faster-whisper ('{STT_MODEL_SIZE}' on {STT_DEVICE})...")
        self.model = WhisperModel(
            STT_MODEL_SIZE,
            device=STT_DEVICE,
            compute_type=STT_COMPUTE_TYPE
        )
        print("[STT] Speech model loaded and ready.")

    def record_push_to_talk(self) -> np.ndarray:
        """
        Records audio from the selected microphone starting when the user hits Enter,
        and stopping when the user hits Enter again.
        """
        input("\n[MIC] Press [ENTER] to START recording...")
        print("[MIC] >>> Recording... Speak your command now. <<<")

        audio_frames = []
        stop_event = threading.Event()

        def audio_callback(indata, frames, time_info, status):
            if status:
                print(f"[MIC Warning] {status}", flush=True)
            audio_frames.append(indata.copy())

        # Direct the stream to the specified hardware device index
        stream = sd.InputStream(
            device=AUDIO_INPUT_DEVICE,
            samplerate=AUDIO_SAMPLE_RATE,
            channels=1,
            dtype="float32",
            callback=audio_callback
        )

        with stream:
            input("[MIC] Press [ENTER] again to STOP recording...")
            stop_event.set()

        print("[MIC] Recording stopped. Processing audio...")

        if not audio_frames:
            return np.array([], dtype=np.float32)

        audio_data = np.concatenate(audio_frames, axis=0).flatten()
        return audio_data

    def transcribe(self, audio_data: np.ndarray) -> str:
        """
        Transcribes the recorded 1D float32 audio array to text.
        """
        if audio_data.size == 0:
            return ""

        segments, info = self.model.transcribe(
            audio_data,
            beam_size=5,
            language="en",
            vad_filter=True
        )

        transcribed_text = " ".join([segment.text for segment in segments]).strip()
        return transcribed_text

    def listen_and_transcribe(self) -> str:
        """
        Convenience pipeline: records user input and returns the transcribed text.
        """
        audio = self.record_push_to_talk()
        if len(audio) == 0:
            return ""
        return self.transcribe(audio)