"""
Phase 6 Smoke Test: Verifying Windows SAPI5 Speech Synthesis
"""
from agent.speech.tts import TextToSpeech

def test_speech():
    print("=== STARTING VOICEPILOT PHASE 6 TTS TEST ===")
    tts = TextToSpeech()
    tts.speak("VoicePilot speech synthesis engine is operational and ready for presentation.")
    print("=== PHASE 6 TTS TEST COMPLETE ===")

if __name__ == "__main__":
    test_speech()