"""
VoicePilot Phase 7 Verification
Tests conversational memory and anaphora resolution ("Open Chrome" -> "Close it").
"""
from agent.brain.llm import LLMBrain
from agent.memory.context import ShortTermMemory

def test_memory_resolution():
    print("=== STARTING VOICEPILOT PHASE 7 MEMORY TEST ===")
    brain = LLMBrain()
    memory = ShortTermMemory()

    # Step 1: Initial command
    cmd1 = "Open Chrome"
    print(f"\n[TURN 1 COMMAND]: \"{cmd1}\"")
    plan1 = brain.plan(cmd1, context=memory.get_context_summary())
    print(f"Thought: {plan1.thought}")
    print(f"Action:  {plan1.steps[0].action} | Target: {plan1.steps[0].target}")

    # Record turn 1 into memory
    memory.record_turn(
        user_command=cmd1,
        thought=plan1.thought,
        steps=[s.model_dump() for s in plan1.steps],
        spoken=plan1.spoken_response
    )

    # Step 2: Referential follow-up command using "it"
    cmd2 = "Close it"
    print(f"\n[TURN 2 COMMAND]: \"{cmd2}\"")
    plan2 = brain.plan(cmd2, context=memory.get_context_summary())
    print(f"Thought: {plan2.thought}")
    print(f"Action:  {plan2.steps[0].action} | Target: {plan2.steps[0].target}")

    # Assertions
    assert plan2.steps[0].action == "terminate_app", "Failed to resolve action to terminate_app"
    assert "chrome" in (plan2.steps[0].target or "").lower(), f"Failed to resolve 'it' to chrome! Got: {plan2.steps[0].target}"

    print("\n=== PHASE 7 MEMORY TEST PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    test_memory_resolution()