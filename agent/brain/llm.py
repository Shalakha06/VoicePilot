"""
LLM Client bridge for VoicePilot.
Uses raw HTTP via requests for complete independence from external vendor SDKs.
"""
import os
import json
import requests
from dotenv import load_dotenv
from agent.brain.prompts import build_system_prompt
from agent.brain.schemas import Plan

# Load environment variables from .env
load_dotenv(override=True)

BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")
API_KEY = os.getenv("LLM_API_KEY", "").strip()
MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-20b").strip()


class LLMBrain:
    def __init__(self):
        if not API_KEY or "your_api_key_here" in API_KEY:
            raise ValueError(
                "[LLM] Error: Valid LLM_API_KEY not found in .env. Please set your Groq key."
            )
        self.endpoint = f"{BASE_URL}/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

    def plan(self, user_command: str, context: str = "") -> Plan:
        """
        Sends user command and conversation context to LLM and validates the output schema.
        """
        system_content = build_system_prompt(context)

        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_command}
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }

        try:
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json=payload,
                timeout=15
            )

            if response.status_code != 200:
                print(f"\n[LLM Debug] Status Code: {response.status_code}")
                print(f"[LLM Debug] Server message: {response.text}")
                response.raise_for_status()

            raw_content = response.json()["choices"][0]["message"]["content"]
            parsed_json = json.loads(raw_content)
            validated_plan = Plan(**parsed_json)
            return validated_plan

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"[LLM] Network or API failure: {str(e)}")
        except (json.JSONDecodeError, Exception) as e:
            raise ValueError(f"[LLM] Validation failed on response: {str(e)}")