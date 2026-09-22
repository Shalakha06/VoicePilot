"""
Text-to-Speech module for VoicePilot.
Uses the native Windows SAPI5 speech engine via pyttsx3.
"""
import pyttsx3

class TextToSpeech:
    def __init__(self, rate: int = 190, volume: float = 1.0):
        """
        Initializes the Windows offline speech synthesizer.
        rate: words per minute (default 190 is natural and brisk)
        volume: 0.0 to 1.0
        """
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", volume)

        # Select a clean system voice if available
        voices = self.engine.getProperty("voices")
        if voices:
            # Typically voices[0] is Microsoft David, voices[1] is Microsoft Zira
            self.engine.setProperty("voice", voices[0].id)

    def speak(self, text: str):
        """
        Synthesizes speech and blocks until utterance completes.
        """
        if not text or not text.strip():
            return
        print(f"[VoicePilot Spoken]: \"{text}\"")
        self.engine.say(text)
        self.engine.runAndWait()