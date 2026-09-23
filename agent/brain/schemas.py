"""
Pydantic Schemas for deterministic LLM output validation.
"""
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

ActionType = Literal[
    "launch_app",
    "terminate_app",
    "open_url",
    "search_web",
    "capture_screen",
    "type_text",
    "press_key",
    "general_response",
    "compose_email",
    "send_whatsapp",
    "calculate",
    "set_alarm_timer",
    "open_calendar",
    "open_settings_panel",
    "play_spotify",
    "set_brightness",
    "join_meet",
    "adjust_volume"
]


class ActionStep(BaseModel):
    action: ActionType = Field(..., description="The low-level tool action to execute.")
    target: Optional[str] = Field(default=None, description="The primary entity target.")
    params: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary parameters.")


class Plan(BaseModel):
    thought: str = Field(..., description="Concise rationale explaining steps.")
    steps: List[ActionStep] = Field(..., description="Ordered action steps.")
    spoken_response: str = Field(..., description="Natural language feedback to speak aloud.")