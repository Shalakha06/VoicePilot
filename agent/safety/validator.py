"""
Safety Validator for VoicePilot.
Intercepts action steps before tool execution to enforce safety constraints.
"""
from typing import Tuple
from agent.brain.schemas import ActionStep
from agent.safety.policies import SafetyLevel, BLOCKED_TERMINATION_TARGETS, CONFIRM_REQUIRED_ACTIONS


class SafetyValidator:
    def __init__(self):
        pass

    def evaluate(self, step: ActionStep) -> Tuple[SafetyLevel, str]:
        """
        Evaluates an ActionStep and returns (SafetyLevel, reason).
        """
        action = step.action
        target = (step.target or "").strip().lower()

        # 1. Check for blocked system operations
        if action == "terminate_app":
            if target in BLOCKED_TERMINATION_TARGETS:
                return (
                    SafetyLevel.BLOCKED,
                    f"Terminating critical system process '{target}' is strictly forbidden."
                )

        # 2. Check for actions requiring user confirmation
        if action in CONFIRM_REQUIRED_ACTIONS:
            return (
                SafetyLevel.CONFIRM_REQUIRED,
                f"Closing application '{target}' may cause loss of unsaved work."
            )

        # 3. Default to SAFE for standard tools
        return (SafetyLevel.SAFE, "Operation is safe to proceed.")

    def request_confirmation(self, message: str) -> bool:
        """
        Prompts the user for explicit confirmation via the console.
        (In future phases, this can also prompt via voice).
        """
        print(f"\n[SAFETY ALERT] {message}")
        choice = input("Proceed? [y/N]: ").strip().lower()
        return choice in ("y", "yes")