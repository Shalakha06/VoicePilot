"""
Central Tool Executor for VoicePilot.
Validates safety before dispatching to system tools.
"""
from typing import Dict, Any, List
from agent.brain.schemas import ActionStep, Plan
from agent.safety.validator import SafetyValidator
from agent.safety.policies import SafetyLevel
from agent.tools.app_control import launch_app, terminate_app
from agent.tools.browser import open_url, search_web, compose_email, send_whatsapp_message
from agent.tools.system import (
    capture_screen, type_text, press_key,
    calculate, set_alarm_or_timer, open_calendar,
    open_settings_panel, control_media_or_spotify,
    set_screen_brightness, join_google_meet,
    adjust_volume
)
from agent.tools.base import tool_response


class ToolExecutor:
    def __init__(self):
        self.safety = SafetyValidator()
        self._registry = {
            "launch_app": self._exec_launch_app,
            "terminate_app": self._exec_terminate_app,
            "open_url": self._exec_open_url,
            "search_web": self._exec_search_web,
            "capture_screen": self._exec_capture_screen,
            "type_text": self._exec_type_text,
            "press_key": self._exec_press_key,
            "general_response": self._exec_general_response,
            "compose_email": self._exec_compose_email,
            "send_whatsapp": self._exec_send_whatsapp,
            "calculate": self._exec_calculate,
            "set_alarm_timer": self._exec_alarm_timer,
            "open_calendar": self._exec_calendar,
            "open_settings_panel": self._exec_settings_panel,
            "play_spotify": self._exec_spotify,
            "set_brightness": self._exec_brightness,
            "join_meet": self._exec_join_meet,
            "adjust_volume": self._exec_adjust_volume,
        }

    def execute_plan(self, plan: Plan) -> List[Dict[str, Any]]:
        results = []
        for step in plan.steps:
            res = self.execute_step(step)
            results.append({"action": step.action, "result": res})
            if not res.get("success", False) and res.get("status") in ["BLOCKED", "CONFIRMATION_REJECTED"]:
                print(f"[Executor] Halting remaining steps: {res.get('message')}")
                break
        return results

    def execute_step(self, step: ActionStep) -> Dict[str, Any]:
        level, reason = self.safety.evaluate(step)

        if level == SafetyLevel.BLOCKED:
            print(f"\n[SAFETY BLOCKED]: {reason}")
            return {"success": False, "status": "BLOCKED", "message": reason, "data": None}

        if level == SafetyLevel.CONFIRM_REQUIRED:
            confirmed = self.safety.request_confirmation(reason)
            if not confirmed:
                print("[SAFETY] Action rejected by user.")
                return {"success": False, "status": "CONFIRMATION_REJECTED", "message": "Cancelled by user.", "data": None}

        handler = self._registry.get(step.action)
        if not handler:
            return tool_response(False, f"Unrecognized action: '{step.action}'")

        try:
            return handler(step)
        except Exception as e:
            return tool_response(False, f"Execution failed on '{step.action}': {str(e)}")

    def _exec_launch_app(self, step: ActionStep) -> Dict[str, Any]:
        return launch_app(step.target)

    def _exec_terminate_app(self, step: ActionStep) -> Dict[str, Any]:
        force = step.params.get("force", False)
        return terminate_app(step.target, force=force)

    def _exec_open_url(self, step: ActionStep) -> Dict[str, Any]:
        url = step.params.get("url") or step.target
        return open_url(url)

    def _exec_search_web(self, step: ActionStep) -> Dict[str, Any]:
        query = step.params.get("query") or step.target
        engine = step.params.get("engine", "google")
        return search_web(query, engine=engine)

    def _exec_capture_screen(self, step: ActionStep) -> Dict[str, Any]:
        prefix = step.params.get("filename_prefix", "screenshot")
        return capture_screen(filename_prefix=prefix)

    def _exec_type_text(self, step: ActionStep) -> Dict[str, Any]:
        text = step.params.get("text", "")
        return type_text(text)

    def _exec_press_key(self, step: ActionStep) -> Dict[str, Any]:
        key = step.target or step.params.get("key", "")
        return press_key(key)

    def _exec_general_response(self, step: ActionStep) -> Dict[str, Any]:
        return tool_response(True, "General response processed.")

    def _exec_compose_email(self, step: ActionStep) -> Dict[str, Any]:
        return compose_email(
            recipient=step.params.get("recipient", ""),
            subject=step.params.get("subject", ""),
            body=step.params.get("body", "")
        )

    def _exec_send_whatsapp(self, step: ActionStep) -> Dict[str, Any]:
        text = step.params.get("text", "") or step.target or ""
        recipient = step.params.get("recipient", "")
        phone = step.params.get("phone", "")
        return send_whatsapp_message(text=text, recipient=recipient, phone=phone)

    def _exec_calculate(self, step: ActionStep) -> Dict[str, Any]:
        expr = step.params.get("expression") or step.target or ""
        return calculate(expr)

    def _exec_alarm_timer(self, step: ActionStep) -> Dict[str, Any]:
        minutes = int(step.params.get("minutes", 0))
        label = step.params.get("label", "Timer")
        return set_alarm_or_timer(minutes=minutes, label=label)

    def _exec_calendar(self, step: ActionStep) -> Dict[str, Any]:
        title = step.params.get("title") or step.target or ""
        return open_calendar(title=title)

    def _exec_settings_panel(self, step: ActionStep) -> Dict[str, Any]:
        panel = step.target or step.params.get("panel", "wifi")
        return open_settings_panel(panel)

    def _exec_spotify(self, step: ActionStep) -> Dict[str, Any]:
        query = step.params.get("query") or step.target or ""
        return control_media_or_spotify(query=query)

    def _exec_brightness(self, step: ActionStep) -> Dict[str, Any]:
        level = step.params.get("level", 50)
        return set_screen_brightness(level=level)

    def _exec_join_meet(self, step: ActionStep) -> Dict[str, Any]:
        code = step.params.get("code") or step.target or ""
        return join_google_meet(code)

    def _exec_adjust_volume(self, step: ActionStep) -> Dict[str, Any]:
        action = step.params.get("action") or step.target or "up"
        level = step.params.get("level")
        return adjust_volume(action=action, level=level)