"""
Browser and Web navigation tools for VoicePilot.
Uses native OS start dispatch to avoid process locks.
"""
import os
import urllib.parse
from agent.tools.base import tool_response

CONTACTS = {
    "rohan": {"phone": "919876543210", "email": "rohan@example.com"},
    "mom": {"phone": "919876543211", "email": "mom@example.com"},
    "self": {"phone": "919876543210", "email": "self@example.com"},
    "professor": {"phone": "", "email": "prof@college.edu"}
}


def resolve_contact(name_or_identifier: str) -> dict:
    if not name_or_identifier:
        return {}
    return CONTACTS.get(name_or_identifier.strip().lower(), {})


def open_url(url: str) -> dict:
    if not url:
        return tool_response(False, "No URL provided.")
    target = url.strip()
    if not target.startswith(("http://", "https://")):
        target = f"https://{target}"
    try:
        os.system(f'start "" "{target}"')
        return tool_response(True, f"Opened URL: {target}")
    except Exception as e:
        return tool_response(False, f"Failed to open URL: {str(e)}")


def search_web(query: str, engine: str = "google") -> dict:
    if not query:
        return tool_response(False, "No search query provided.")
    encoded = urllib.parse.quote_plus(query.strip())
    url = f"https://www.google.com/search?q={encoded}"
    return open_url(url)


def compose_email(recipient: str = "", subject: str = "", body: str = "") -> dict:
    contact = resolve_contact(recipient)
    if contact and contact.get("email"):
        recipient = contact["email"]

    params = {"view": "cm", "fs": "1"}
    if recipient: params["to"] = recipient
    if subject: params["su"] = subject
    if body: params["body"] = body

    url = f"https://mail.google.com/mail/?{urllib.parse.urlencode(params)}"
    return open_url(url)


def send_whatsapp_message(text: str, recipient: str = "", phone: str = "") -> dict:
    if not text:
        return tool_response(False, "No message content provided for WhatsApp.")

    target_phone = phone.strip() if phone else ""
    if recipient and not target_phone:
        contact = resolve_contact(recipient)
        if contact and contact.get("phone"):
            target_phone = contact["phone"]
        elif recipient.replace("+", "").replace(" ", "").isdigit():
            target_phone = recipient

    clean_phone = "".join(filter(str.isdigit, target_phone))
    encoded_text = urllib.parse.quote(text)

    if clean_phone:
        url = f"https://api.whatsapp.com/send?phone={clean_phone}&text={encoded_text}"
    else:
        url = f"https://api.whatsapp.com/send?text={encoded_text}"

    return open_url(url)