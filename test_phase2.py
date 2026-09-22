"""
VoicePilot Phase 2 Smoke Test
Verifies microphone audio capture and local transcription with faster-whisper.
"""
from agent.speech.stt import SpeechToText

def run_test():
    print("=== STARTING VOICEPILOT PHASE 2 STT TEST ===")
    
    stt = SpeechToText()

    print("\nWe will now run a voice recording test.")
    print("When prompted:")
    print("1. Press Enter.")
    print("2. Clearly say: 'Open Chrome and search for machine learning tutorials'")
    print("3. Press Enter to finish.")

    transcript = stt.listen_and_transcribe()

    print("\n-------------------------------------------")
    print(f"TRANSCRIPTION RESULT: \"{transcript}\"")
    print("-------------------------------------------")

    if transcript:
        print("\n=== PHASE 2 STT TEST PASSED SUCCESSFULLY ===")
    else:
        print("\n[!] No speech detected. Please check your microphone input settings.")

if __name__ == "__main__":
    run_test()