"""
Central Tool Executor for VoicePilot with integrated Safety Verification.
"""
from typing import Dict, Any, List

from agent.brain.schemas import ActionStep, Plan
from agent.tools.base import tool_response
from agent.tools.app_control import launch_app, terminate_app
from agent.tools.browser import open_url, search_web
from agent.tools.system import capture_screen, type_text, press_key
from agent.safety.validator import SafetyValidator
from agent.safety.policies import SafetyLevel


class ToolExecutor:
    def __init__(self):
        self.validator = SafetyValidator()
        self._registry = {
            "launch_app": self._exec_launch_app,
            "terminate_app": self._exec_terminate_app,
            "open_url": self._exec_open_url,
            "search_web": self._exec_search_web,
            "capture_screen": self._exec_capture_screen,
            "type_text": self._exec_type_text,
            "press_key": self._exec_press_key,
            "general_response": self._exec_general_response
        }

    def execute_step(self, step: ActionStep) -> Dict[str, Any]:
        """
        Validates safety constraints before executing an ActionStep.
        """
        level, reason = self.validator.evaluate(step)

        # Tier 3: Blocked actions are dropped immediately
        if level == SafetyLevel.BLOCKED:
            return tool_response(
                success=False,
                message=f"[SAFETY BLOCKED] {reason}"
            )

        # Tier 2: Confirm-required actions prompt the user
        if level == SafetyLevel.CONFIRM_REQUIRED:
            confirmed = self.validator.request_confirmation(reason)
            if not confirmed:
                return tool_response(
                    success=False,
                    message="Operation cancelled by user."
                )

        # Tier 1: Safe actions proceed to handler
        handler = self._registry.get(step.action)
        if not handler:
            return tool_response(
                success=False,
                message=f"Action '{step.action}' is not registered."
            )

        try:
            return handler(step)
        except Exception as e:
            return tool_response(
                success=False,
                message=f"Unhandled error in '{step.action}': {str(e)}"
            )

    def execute_plan(self, plan: Plan) -> List[Dict[str, Any]]:
        results = []
        for step in plan.steps:
            res = self.execute_step(step)
            results.append({
                "action": step.action,
                "target": step.target,
                "result": res
            })

            if not res["success"] and step.action != "general_response":
                print(f"[Executor] Step '{step.action}' stopped/failed: {res['message']}")

        return results

    # --- Tool Bridges ---
    def _exec_launch_app(self, step: ActionStep) -> Dict[str, Any]:
        if not step.target:
            return tool_response(False, "Missing target application name.")
        return launch_app(step.target)

    def _exec_terminate_app(self, step: ActionStep) -> Dict[str, Any]:
        if not step.target:
            return tool_response(False, "Missing target application name to close.")
        return terminate_app(step.target)

    def _exec_open_url(self, step: ActionStep) -> Dict[str, Any]:
        url = step.params.get("url") or step.target
        if not url:
            return tool_response(False, "Missing target URL.")
        return open_url(url)

    def _exec_search_web(self, step: ActionStep) -> Dict[str, Any]:
        query = step.params.get("query") or step.target or ""
        return search_web(query)

    def _exec_capture_screen(self, step: ActionStep) -> Dict[str, Any]:
        prefix = step.params.get("filename_prefix", "shot")
        return capture_screen(prefix)

    def _exec_type_text(self, step: ActionStep) -> Dict[str, Any]:
        text = step.params.get("text", "")
        return type_text(text)

    def _exec_press_key(self, step: ActionStep) -> Dict[str, Any]:
        key = step.target or step.params.get("key", "")
        return press_key(key)

    def _exec_general_response(self, step: ActionStep) -> Dict[str, Any]:
        return tool_response(True, "Informational query handled directly.")