"""
Text-to-Speech engine using pyttsx3 with Windows SAPI5 driver recovery.
"""
import pyttsx3


class TextToSpeech:
    def __init__(self, rate: int = 180, volume: float = 1.0):
        self.rate = rate
        self.volume = volume

    def speak(self, text: str):
        if not text:
            return
        
        print(f"\n[VOICEPILOT SPEAKING]: \"{text}\"")
        
        try:
            # Re-initialize on each call to prevent SAPI5 silent deadlock
            engine = pyttsx3.init("sapi5")
            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", self.volume)

            # Select a clear Windows system voice
            voices = engine.getProperty("voices")
            for voice in voices:
                if "zira" in voice.name.lower() or "david" in voice.name.lower():
                    engine.setProperty("voice", voice.id)
                    break

            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(f"[TTS Warning]: Could not play audio via pyttsx3: {e}")