"""
Application process management tools for VoicePilot.
Launches and terminates Windows processes with fallback path discovery.
"""
import os
import subprocess
import psutil
from agent.tools.base import tool_response

# Common Windows install locations for standard apps
KNOWN_APP_PATHS = {
    "chrome": [
        os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
    ],
    "edge": [
        os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
        os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
    ],
    "notepad": ["notepad.exe"],
    "calc": ["calc.exe"],
    "calculator": ["calc.exe"],
    "spotify": [
        os.path.expandvars(r"%AppData%\Spotify\Spotify.exe"),
    ]
}


def launch_app(app_name: str) -> dict:
    if not app_name:
        return tool_response(False, "No application name specified.")

    clean_name = app_name.lower().strip().replace(".exe", "")

    # 1. Check known absolute paths for browsers / major apps
    if clean_name in KNOWN_APP_PATHS:
        for path in KNOWN_APP_PATHS[clean_name]:
            if os.path.exists(path):
                try:
                    subprocess.Popen([path], shell=False)
                    return tool_response(True, f"Launched {clean_name.capitalize()} successfully.")
                except Exception:
                    pass

    # 2. Try Windows Shell 'start' (works for apps registered in App Paths)
    try:
        os.system(f'start "" "{clean_name}"')
        return tool_response(True, f"Launched {clean_name}.")
    except Exception:
        pass

    # 3. Direct subprocess fallback
    try:
        subprocess.Popen([clean_name], shell=True)
        return tool_response(True, f"Launched {clean_name}.")
    except Exception as e:
        return tool_response(False, f"Failed to launch '{app_name}': {str(e)}")


def terminate_app(app_name: str, force: bool = False) -> dict:
    if not app_name:
        return tool_response(False, "No application name specified to terminate.")

    target = app_name.lower().strip().replace(".exe", "")
    terminated_count = 0

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            p_name = proc.info['name'].lower().replace(".exe", "")
            if target in p_name:
                if force:
                    proc.kill()
                else:
                    proc.terminate()
                terminated_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if terminated_count > 0:
        return tool_response(True, f"Closed {terminated_count} process(es) matching '{app_name}'.")
    return tool_response(False, f"No running application found matching '{app_name}'.")