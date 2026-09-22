"""
VoicePilot Phase 1 Smoke Test
Verifies all core deterministic desktop control tools.
"""
import time
from agent.tools.app_control import launch_app, terminate_app
from agent.tools.browser import search_web
from agent.tools.system import capture_screen, type_text, press_key

def run_tests():
    print("=== STARTING VOICEPILOT PHASE 1 TOOL VERIFICATION ===")

    # Test 1: Launch Notepad
    print("\n[1] Testing launch_app('notepad')...")
    res1 = launch_app("notepad")
    print("Result:", res1)
    assert res1["success"], "Failed to launch Notepad"

    # Allow Notepad window to open and receive OS focus
    time.sleep(1.5)

    # Test 2: Typing text into Notepad
    print("\n[2] Testing type_text('VoicePilot Desktop Agent Active.')...")
    res2 = type_text("VoicePilot Desktop Agent Active.\n")
    print("Result:", res2)

    # Test 3: Take a screenshot
    print("\n[3] Testing capture_screen()...")
    res3 = capture_screen("voicepilot_phase1_test")
    print("Result:", res3)
    assert res3["success"], "Failed to capture screenshot"

    # Test 4: Web Search
    print("\n[4] Testing search_web('Python os automation')...")
    res4 = search_web("Python os automation")
    print("Result:", res4)
    assert res4["success"], "Failed to open web search"

    # Test 5: Terminate Notepad
    print("\n[5] Testing terminate_app('notepad')...")
    time.sleep(1.0)
    res5 = terminate_app("notepad")
    print("Result:", res5)
    assert res5["success"], "Failed to terminate Notepad"

    print("\n=== ALL VOICEPILOT PHASE 1 TOOL TESTS COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_tests()