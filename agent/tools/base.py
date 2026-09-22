"""
Base response model and common abstractions for VoicePilot tools.
"""
from typing import Any, Dict

def tool_response(success: bool, message: str, data: Any = None) -> Dict[str, Any]:
    """
    Constructs a uniform response dictionary for all tools.
    """
    return {
        "success": success,
        "message": message,
        "data": data or {}
    }