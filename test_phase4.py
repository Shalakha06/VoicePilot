"""
VoicePilot Phase 4 Verification
Tests end-to-end translation from user prompt to live desktop execution via ToolExecutor.
"""
import time
from agent.brain.llm import LLMBrain
from agent.tools.executor import ToolExecutor

def run_integration_test():
    print("=== STARTING VOICEPILOT PHASE 4 EXECUTOR INTEGRATION TEST ===")

    brain = LLMBrain()
    executor = ToolExecutor()

    # Compound natural language command to execute live
    command = "Open Notepad, take a screenshot, and close notepad"
    print(f"\n[TEST COMMAND]: \"{command}\"")

    # 1. LLM Plans the actions
    print("[1] Generating plan from LLM...")
    plan = brain.plan(command)
    print(f"Thought: {plan.thought}")
    print(f"Spoken response planned: \"{plan.spoken_response}\"")
    print(f"Plan steps generated: {len(plan.steps)}")

    # 2. Executor executes each step in order
    print("\n[2] Executing plan steps through ToolExecutor...")
    results = executor.execute_plan(plan)

    print("\n[3] Execution Results Summary:")
    for idx, item in enumerate(results, start=1):
        status = "SUCCESS" if item["result"]["success"] else "FAILED"
        print(f"  Step {idx}: [{item['action']}] -> {status}")
        print(f"          Message: {item['result']['message']}")

    print("\n=== PHASE 4 EXECUTOR TEST COMPLETED ===")

if __name__ == "__main__":
    run_integration_test()