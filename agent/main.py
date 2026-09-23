"""
VoicePilot Main Runtime Orchestrator (Direct Terminal Engine)
Bridges STT -> Brain/LLM -> Memory -> Safety -> Tool Execution -> TTS.
"""
import sys
from agent.speech.stt import SpeechToText
from agent.speech.tts import TextToSpeech
from agent.brain.llm import LLMBrain
from agent.tools.executor import ToolExecutor
from agent.memory.context import ShortTermMemory


def print_banner():
    banner = """
============================================================
              VOICEPILOT: AUTONOMOUS DESKTOP AGENT           
============================================================
 [1] Press ENTER to speak.
 [2] Say your command clearly at your own pace.
 [3] Press ENTER to stop recording and execute.
 [*] Type/say 'exit' or 'quit' to shut down.
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
        memory = ShortTermMemory(max_turns=5)
    except Exception as e:
        print(f"\n[FATAL] Subsystem initialization failed: {e}")
        sys.exit(1)

    print_banner()
    tts.speak("VoicePilot is online and standing by.")

    while True:
        try:
            # 1. Flexible Push-to-Talk Speech Capture
            user_command = stt.listen_and_transcribe().strip()

            if not user_command:
                print("[VoicePilot] No clear speech detected. Try again.")
                continue

            print(f"\n[USER COMMAND]: \"{user_command}\"")

            # Check shutdown
            if user_command.lower().rstrip(".") in ["exit", "quit", "stop", "shutdown"]:
                tts.speak("Shutting down VoicePilot. Goodbye.")
                print("[SYSTEM] Session terminated by user.")
                break

            # 2. Plan action using context from ShortTermMemory
            print("[BRAIN] Analyzing intent and formulating execution plan...")
            context_summary = memory.get_context_summary()
            plan = brain.plan(user_command, context=context_summary)
            print(f"[REASONING]: {plan.thought}")

            # 3. Speak verbal feedback
            if plan.spoken_response:
                print(f"[VOICEPILOT]: \"{plan.spoken_response}\"")
                tts.speak(plan.spoken_response)

            # 4. Dispatch steps
            if plan.steps:
                print(f"[EXECUTOR] Executing {len(plan.steps)} planned step(s)...")
                results = executor.execute_plan(plan)
                for idx, item in enumerate(results, start=1):
                    status = "OK" if item["result"]["success"] else "FAILED"
                    print(f"  Step {idx} [{item['action']}]: {status} - {item['result']['message']}")

            # 5. Record memory
            memory.record_turn(
                user_command=user_command,
                thought=plan.thought,
                steps=[s.model_dump() for s in plan.steps],
                spoken=plan.spoken_response
            )

        except KeyboardInterrupt:
            print("\n[SYSTEM] Manual interrupt caught. Exiting safely.")
            tts.speak("Session interrupted. Exiting.")
            break
        except Exception as e:
            print(f"\n[ERROR] Runtime anomaly: {e}")
            tts.speak("An error occurred while processing that request.")


if __name__ == "__main__":
    main()