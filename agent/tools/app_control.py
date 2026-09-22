"""
Application control module: launching and terminating Windows processes.
"""
import subprocess
import psutil
from typing import Dict, Any

from agent.config import APP_ALIASES
from agent.tools.base import tool_response


def launch_app(app_name: str) -> Dict[str, Any]:
    """
    Launches a local Windows application by name or common alias.
    """
    target = app_name.strip().lower()
    binary = APP_ALIASES.get(target, app_name)

    try:
        process = subprocess.Popen(
            binary,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return tool_response(
            success=True,
            message=f"Application '{app_name}' launched successfully.",
            data={"pid": process.pid, "target": binary}
        )
    except Exception as e:
        return tool_response(
            success=False,
            message=f"Failed to launch '{app_name}': {str(e)}"
        )


def terminate_app(app_name: str) -> Dict[str, Any]:
    """
    Finds and gracefully terminates all running processes matching the app_name.
    """
    target = app_name.strip().lower()
    target_bin = APP_ALIASES.get(target, target).lower()
    terminated_pids = []

    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                proc_name = proc.info['name']
                if proc_name and (
                    proc_name.lower() == target_bin or 
                    target in proc_name.lower()
                ):
                    p = psutil.Process(proc.info['pid'])
                    p.terminate()
                    terminated_pids.append(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        if terminated_pids:
            return tool_response(
                success=True,
                message=f"Closed {len(terminated_pids)} instance(s) of '{app_name}'.",
                data={"pids": terminated_pids}
            )
        else:
            return tool_response(
                success=False,
                message=f"No active process found matching '{app_name}'."
            )

    except Exception as e:
        return tool_response(
            success=False,
            message=f"Error occurred while terminating '{app_name}': {str(e)}"
        )