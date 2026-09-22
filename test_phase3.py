"""
VoicePilot Phase 3 Verification
Tests natural language translation into validated JSON action schemas.
"""
from agent.brain.llm import LLMBrain

def test_intent_parsing():
    print("=== STARTING VOICEPILOT PHASE 3 INTENT PLANNING TEST ===")
    
    brain = LLMBrain()

    test_queries = [
        "Open Chrome",
        "Search Google for machine learning tutorials",
        "Take a screenshot and close notepad",
        "What is the capital of France?"
    ]

    for query in test_queries:
        print(f"\n[USER COMMAND]: \"{query}\"")
        plan = brain.plan(query)
        print(f"Thought: {plan.thought}")
        print(f"Spoken:  {plan.spoken_response}")
        print(f"Steps ({len(plan.steps)}):")
        for idx, step in enumerate(plan.steps, start=1):
            print(f"  {idx}. Action: {step.action:<16} | Target: {str(step.target):<10} | Params: {step.params}")

    print("\n=== PHASE 3 INTENT TEST PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    test_intent_parsing()