"""
VoicePilot Phase 5 Verification
Tests safety tiers: SAFE execution, CONFIRM_REQUIRED interception, and BLOCKED rejection.
"""
from agent.brain.schemas import ActionStep
from agent.tools.executor import ToolExecutor

def test_safety_guardrails():
    print("=== STARTING VOICEPILOT PHASE 5 SAFETY TEST ===")
    executor = ToolExecutor()

    # 1. Test BLOCKED action (attempt to kill Windows Explorer)
    print("\n--- Test 1: Evaluating BLOCKED operation (terminate explorer.exe) ---")
    blocked_step = ActionStep(action="terminate_app", target="explorer.exe")
    res1 = executor.execute_step(blocked_step)
    print("Result:", res1)
    assert not res1["success"], "Blocked action was incorrectly allowed!"
    assert "[SAFETY BLOCKED]" in res1["message"]

    # 2. Test SAFE action (take screenshot)
    print("\n--- Test 2: Evaluating SAFE operation (capture_screen) ---")
    safe_step = ActionStep(action="capture_screen", params={"filename_prefix": "safety_test"})
    res2 = executor.execute_step(safe_step)
    print("Result:", res2)
    assert res2["success"], "Safe action failed to execute!"

    # 3. Test CONFIRM_REQUIRED action (close notepad)
    print("\n--- Test 3: Evaluating CONFIRM_REQUIRED operation (terminate notepad) ---")
    print("When prompted below, type 'y' to confirm the closure.")
    confirm_step = ActionStep(action="terminate_app", target="notepad")
    res3 = executor.execute_step(confirm_step)
    print("Result:", res3)

    print("\n=== PHASE 5 SAFETY TEST PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    test_safety_guardrails()