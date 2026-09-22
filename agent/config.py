"""
VoicePilot Configuration
Defines central filesystem paths and application constants.
"""
from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure runtime directories exist
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Common Windows executable aliases (lowercase key -> executable or protocol)
APP_ALIASES = {
    "notepad": "notepad.exe",
    "calc": "calc.exe",
    "calculator": "calc.exe",
    "chrome": "chrome.exe",
    "edge": "msedge.exe",
    "explorer": "explorer.exe",
    "terminal": "wt.exe",
    "cmd": "cmd.exe",
    "vscode": "code.cmd",
    "code": "code.cmd",
    "taskmgr": "taskmgr.exe"
}

"""
VoicePilot Configuration
Defines central filesystem paths and application constants.
"""
from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure runtime directories exist
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Common Windows executable aliases (lowercase key -> executable or protocol)
APP_ALIASES = {
    "notepad": "notepad.exe",
    "calc": "calc.exe",
    "calculator": "calc.exe",
    "chrome": "chrome.exe",
    "edge": "msedge.exe",
    "explorer": "explorer.exe",
    "terminal": "wt.exe",
    "cmd": "cmd.exe",
    "vscode": "code.cmd",
    "code": "code.cmd",
    "taskmgr": "taskmgr.exe"
}

# --- Audio & Speech Configuration ---
# Whisper models: 'tiny.en' (fastest, lowest RAM ~390MB), 'base.en' (balanced, ~500MB)
STT_MODEL_SIZE = "base.en"
# Device: 'cpu' for standard laptops, compute_type 'int8' minimizes CPU load
STT_DEVICE = "cpu"
STT_COMPUTE_TYPE = "int8"
# Standard sampling rate expected by Whisper
AUDIO_SAMPLE_RATE = 16000
# Set explicitly to your real microphone array index
AUDIO_INPUT_DEVICE = 2