"""
System-level operations: screenshots and synthetic input automation.
"""
import time
from datetime import datetime
from typing import Dict, Any
import pyautogui

from agent.config import SCREENSHOTS_DIR
from agent.tools.base import tool_response

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1


def capture_screen(filename_prefix: str = "shot") -> Dict[str, Any]:
    """
    Captures the primary monitor screen and saves it as a timestamped PNG.
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.png"
        filepath = SCREENSHOTS_DIR / filename

        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)

        return tool_response(
            success=True,
            message=f"Screenshot saved to {filename}.",
            data={"filepath": str(filepath)}
        )
    except Exception as e:
        return tool_response(
            success=False,
            message=f"Screen capture failed: {str(e)}"
        )


def type_text(text: str) -> Dict[str, Any]:
    """
    Simulates keyboard entry into the active Windows window.
    """
    try:
        time.sleep(0.5)
        pyautogui.write(text, interval=0.02)
        return tool_response(
            success=True,
            message=f"Typed input of length {len(text)} characters.",
            data={"text": text}
        )
    except Exception as e:
        return tool_response(
            success=False,
            message=f"Typing simulation failed: {str(e)}"
        )


def press_key(key: str) -> Dict[str, Any]:
    """
    Simulates pressing a single key (e.g., 'enter', 'esc', 'space', 'volumedown').
    """
    clean_key = key.strip().lower()
    try:
        pyautogui.press(clean_key)
        return tool_response(
            success=True,
            message=f"Pressed key: {clean_key}.",
            data={"key": clean_key}
        )
    except Exception as e:
        return tool_response(
            success=False,
            message=f"Failed to press key '{key}': {str(e)}"
        )