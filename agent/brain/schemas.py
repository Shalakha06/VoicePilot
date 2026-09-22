"""
Pydantic schemas for VoicePilot structured actions.
"""
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

# Supported tool actions
ActionType = Literal[
    "launch_app",
    "terminate_app",
    "open_url",
    "search_web",
    "capture_screen",
    "type_text",
    "press_key",
    "general_response"
]

class ActionStep(BaseModel):
    """Represents a single atomic operation."""
    action: ActionType = Field(description="The designated tool identifier to execute.")
    target: Optional[str] = Field(default=None, description="App name, key name, or primary entity.")
    params: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary arguments like query or text.")

class Plan(BaseModel):
    """The complete response contract returned by the reasoning engine."""
    thought: str = Field(description="Brief internal explanation of why these steps were chosen.")
    steps: List[ActionStep] = Field(description="Ordered list of actions to satisfy the user request.")
    spoken_response: str = Field(description="Natural, concise voice response to speak to the user.")