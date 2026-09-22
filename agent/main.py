"""
VoicePilot Main Runtime Orchestrator
Bridges STT -> Brain/LLM -> Safety -> Tool Execution -> TTS in a live interactive loop.
"""
import sys
from agent.speech.stt import SpeechToText
from agent.speech.tts import TextToSpeech
from agent.brain.llm import LLMBrain
from agent.tools.executor import ToolExecutor

def print_banner():
    banner = """
============================================================
              VOICEPILOT: AUTONOMOUS DESKTOP AGENT           
============================================================
 [1] Press ENTER to talk (Push-to-Talk).
 [2] Speak your command clearly.
 [3] Press ENTER again to stop recording and process.
 [*] Say or type 'exit' or 'quit' to shut down.
============================================================
"""
    print(banner)

def main():
    print("[INIT] Initializing VoicePilot Subsystems...")
    try:
        stt = SpeechToText()
        tts = TextToSpeech()
        brain = LLMBrain()
        executor = ToolExecutor()
    except Exception as e:
        print(f"\n[FATAL] Subsystem initialization failed: {e}")
        sys.exit(1)

    print_banner()
    tts.speak("VoicePilot is online and standing by.")

    while True:
        try:
            # 1. Capture and transcribe spoken input
            user_command = stt.listen_and_transcribe().strip()

            if not user_command:
                print("\n[VoicePilot] No clear speech detected. Try again.")
                continue

            print(f"\n[USER COMMAND]: \"{user_command}\"")

            # Check for manual termination command
            if user_command.lower() in ["exit", "quit", "stop", "exit."]:
                tts.speak("Shutting down VoicePilot. Goodbye.")
                print("[SYSTEM] Session terminated by user.")
                break

            # 2. Plan the action using the LLM Brain
            print("[BRAIN] Analyzing intent and formulating execution plan...")
            plan = brain.plan(user_command)
            print(f"[REASONING]: {plan.thought}")

            # 3. Speak the feedback immediately
            if plan.spoken_response:
                tts.speak(plan.spoken_response)

            # 4. Dispatch the planned steps through Safety & Executor
            if plan.steps:
                print(f"[EXECUTOR] Executing {len(plan.steps)} planned step(s)...")
                results = executor.execute_plan(plan)
                
                # Print clean execution telemetry
                for idx, item in enumerate(results, start=1):
                    status = "OK" if item["result"]["success"] else "FAILED"
                    print(f"  Step {idx} [{item['action']}]: {status} - {item['result']['message']}")

        except KeyboardInterrupt:
            print("\n[SYSTEM] Manual interrupt caught. Exiting safely.")
            tts.speak("Session interrupted. Exiting.")
            break
        except Exception as e:
            print(f"\n[ERROR] Runtime anomaly in main loop: {e}")
            tts.speak("An error occurred while processing that request.")

if __name__ == "__main__":
    main()
    