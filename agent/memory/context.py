"""
Short-term Conversation Memory for VoicePilot.
Maintains a sliding window of recent user utterances and assistant actions.
"""
from typing import List, Dict, Any
from collections import deque

class ShortTermMemory:
    def __init__(self, max_turns: int = 5):
        """
        max_turns: Number of interaction pairs (user command + plan) to remember.
        """
        self.history = deque(maxlen=max_turns)

    def record_turn(self, user_command: str, thought: str, steps: List[Dict[str, Any]], spoken: str):
        """
        Appends the latest interaction to the memory buffer.
        """
        self.history.append({
            "user": user_command,
            "thought": thought,
            "steps": steps,
            "spoken": spoken
        })

    def get_context_summary(self) -> str:
        """
        Formats recent turns into a concise context block for the LLM system prompt.
        """
        if not self.history:
            return "No previous conversational context."

        context_lines = []
        for idx, turn in enumerate(self.history, start=1):
            actions_summary = ", ".join(
                [f"{s.get('action')}(target={s.get('target')})" for s in turn.get("steps", [])]
            ) or "None"
            context_lines.append(
                f"Turn {idx}: User='{turn['user']}' | Executed=[{actions_summary}] | VoicePilot='{turn['spoken']}'"
            )
        return "\n".join(context_lines)

    def clear(self):
        """Resets the memory buffer."""
        self.history.clear()