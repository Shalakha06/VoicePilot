import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

api_key = os.getenv("LLM_API_KEY", "").strip()
url = "https://api.groq.com/openai/v1/models"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)
print("Status Code:", response.status_code)

if response.status_code == 200:
    data = response.json()
    print("\nModels available on your key:")
    for m in data.get("data", []):
        print(" -", m["id"])
else:
    print("Error response:", response.text)