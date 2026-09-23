"""
System-level automation tools for VoicePilot.
Handles volume, display, keyboard, audio, panels, calculator, calendar, alarms, Spotify, and settings.
"""
import os
import time
import math
import subprocess
import threading
import pyautogui
from datetime import datetime
from agent.tools.base import tool_response

SCREENSHOT_DIR = "screenshots"


def adjust_volume(action: str = "up", level: int = None) -> dict:
    """
    Direct Windows Master Volume Control via pycaw (compatible with both modern and legacy pycaw versions).
    Supports exact percentages (0-100), relative steps (up/down), and mute/unmute.
    """
    try:
        from pycaw.pycaw import AudioUtilities

        device = AudioUtilities.GetSpeakers()

        # Handle modern AudioDevice wrapper or fallback to legacy COM interface
        if hasattr(device, "EndpointVolume"):
            volume = device.EndpointVolume
        elif hasattr(device, "Activate"):
            from comtypes import CLSCTX_ALL
            from ctypes import cast, POINTER
            from pycaw.pycaw import IAudioEndpointVolume
            interface = device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
        else:
            return tool_response(False, "Unsupported pycaw device object.")

        act = action.lower().strip() if action else "up"

        # 1. Exact Percentage (0 to 100)
        if level is not None:
            pct = max(0, min(100, int(level)))
            volume.SetMasterVolumeLevelScalar(pct / 100.0, None)
            return tool_response(True, f"Master volume set to {pct}%.")

        # 2. Step Up (~10%)
        if act in ["up", "increase", "raise", "higher"]:
            current = volume.GetMasterVolumeLevelScalar()
            new_vol = min(1.0, current + 0.10)
            volume.SetMasterVolumeLevelScalar(new_vol, None)
            return tool_response(True, f"Volume increased to {int(round(new_vol * 100))}%.")

        # 3. Step Down (~10%)
        elif act in ["down", "decrease", "lower"]:
            current = volume.GetMasterVolumeLevelScalar()
            new_vol = max(0.0, current - 0.10)
            volume.SetMasterVolumeLevelScalar(new_vol, None)
            return tool_response(True, f"Volume decreased to {int(round(new_vol * 100))}%.")

        # 4. Mute
        elif act in ["mute", "silence"]:
            volume.SetMute(1, None)
            return tool_response(True, "Master audio muted.")

        # 5. Unmute
        elif act in ["unmute"]:
            volume.SetMute(0, None)
            return tool_response(True, "Master audio unmuted.")

        else:
            return tool_response(False, f"Unrecognized volume action: '{action}'")

    except Exception as e:
        return tool_response(False, f"Failed to control system audio: {str(e)}")


def capture_screen(filename_prefix: str = "screenshot") -> dict:
    try:
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(SCREENSHOT_DIR, f"{filename_prefix}_{timestamp}.png")
        pyautogui.screenshot().save(filepath)
        return tool_response(True, f"Screenshot saved at {filepath}", data={"filepath": filepath})
    except Exception as e:
        return tool_response(False, f"Failed to capture screen: {str(e)}")


def type_text(text: str, interval: float = 0.03) -> dict:
    if not text:
        return tool_response(False, "No text provided to type.")
    try:
        time.sleep(0.6)  # Pause to ensure target app has focus
        pyautogui.write(text, interval=interval)
        return tool_response(True, f"Typed: '{text}'")
    except Exception as e:
        return tool_response(False, f"Failed to type: {str(e)}")


def press_key(key: str) -> dict:
    if not key:
        return tool_response(False, "No key provided.")
    try:
        pyautogui.press(key.strip().lower())
        return tool_response(True, f"Pressed key '{key}'")
    except Exception as e:
        return tool_response(False, f"Failed to press key: {str(e)}")


def calculate(expression: str) -> dict:
    if not expression or expression.strip().lower() in ["app", "open", "calculator"]:
        os.system("start calc.exe")
        return tool_response(True, "Opened Windows Calculator.")

    clean_expr = expression.replace("^", "**").replace("x", "*").replace("÷", "/")
    safe_dict = {
        "abs": abs,
        "round": round,
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "pi": math.pi,
        "e": math.e,
    }
    try:
        res = eval(clean_expr, {"__builtins__": None}, safe_dict)
        return tool_response(True, f"The answer is {res}", data={"result": res})
    except Exception:
        os.system("start calc.exe")
        return tool_response(True, "Opened Calculator app.")


def set_alarm_or_timer(minutes: int = 0, label: str = "Timer") -> dict:
    try:
        if minutes > 0:
            os.system("start ms-clock:timer")

            def countdown():
                time.sleep(minutes * 60)
                import winsound

                for _ in range(4):
                    winsound.Beep(1200, 400)
                    time.sleep(0.2)

            threading.Thread(target=countdown, daemon=True).start()
            return tool_response(True, f"Timer set for {minutes} minute(s).")
        os.system("start ms-clock:alarm")
        return tool_response(True, "Opened Windows Alarms.")
    except Exception as e:
        return tool_response(False, f"Alarm/Timer error: {str(e)}")


def open_calendar(title: str = "") -> dict:
    try:
        if title:
            import urllib.parse

            url = f"https://calendar.google.com/calendar/u/0/r/eventedit?text={urllib.parse.quote(title)}"
            os.system(f'start "" "{url}"')
            return tool_response(True, f"Drafted calendar event: '{title}'")
        os.system("start outlookcal:")
        return tool_response(True, "Opened Windows Calendar.")
    except Exception as e:
        return tool_response(False, f"Calendar error: {str(e)}")


def open_settings_panel(panel: str) -> dict:
    target = panel.lower().strip()
    try:
        if "wifi" in target or "network" in target or "internet" in target:
            os.system("start ms-availablenetworks:")
            return tool_response(True, "Opened Wi-Fi connections drawer.")
        elif "bluetooth" in target or "bt" in target:
            os.system("start ms-settings:bluetooth")
            return tool_response(True, "Opened Bluetooth settings.")
        else:
            pyautogui.hotkey("win", "a")
            return tool_response(True, "Opened Windows Quick Settings.")
    except Exception as e:
        return tool_response(False, f"Failed to open {panel} settings: {str(e)}")


def join_google_meet(code_or_url: str = "") -> dict:
    try:
        code = code_or_url.strip()
        if code and code.startswith("http"):
            url = code
        elif code:
            url = f"https://meet.google.com/{code}"
        else:
            url = "https://meet.google.com/new"

        os.system(f'start "" "{url}"')
        return tool_response(True, f"Opened Google Meet: {url}")
    except Exception as e:
        return tool_response(False, f"Failed to open Google Meet: {str(e)}")


def control_media_or_spotify(query: str = "") -> dict:
    try:
        if query:
            import urllib.parse

            encoded = urllib.parse.quote(query)
            os.system(f"start spotify:search:{encoded}")
            return tool_response(True, f"Searched '{query}' on Spotify.")
        pyautogui.press("playpause")
        return tool_response(True, "Toggled playback.")
    except Exception as e:
        return tool_response(False, f"Spotify error: {str(e)}")


def set_screen_brightness(level: int = 50) -> dict:
    try:
        level = max(0, min(100, int(level)))
        ps_cmd = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})"
        subprocess.run(
            ["powershell", "-Command", ps_cmd],
            capture_output=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return tool_response(True, f"Screen brightness set to {level}%.")
    except Exception:
        try:
            import screen_brightness_control as sbc

            sbc.set_brightness(level)
            return tool_response(True, f"Screen brightness set to {level}%.")
        except Exception as e:
            return tool_response(False, f"Failed to change brightness: {str(e)}")