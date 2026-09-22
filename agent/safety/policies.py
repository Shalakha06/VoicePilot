"""
Security policies and permission boundaries for VoicePilot.
"""
from enum import Enum

class SafetyLevel(Enum):
    SAFE = "SAFE"
    CONFIRM_REQUIRED = "CONFIRM_REQUIRED"
    BLOCKED = "BLOCKED"

# Windows critical system processes that must NEVER be terminated
BLOCKED_TERMINATION_TARGETS = {
    "explorer", "explorer.exe",
    "svchost", "svchost.exe",
    "csrss", "csrss.exe",
    "smss", "smss.exe",
    "services", "services.exe",
    "lsass", "lsass.exe",
    "winlogon", "winlogon.exe",
    "system", "system idle process"
}

# Processes or actions that require verbal/text user confirmation
CONFIRM_REQUIRED_ACTIONS = {
    "terminate_app"
}