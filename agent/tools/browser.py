"""
Browser and Web navigation tools for VoicePilot.
"""
import webbrowser
import urllib.parse
from typing import Dict, Any

from agent.tools.base import tool_response


def open_url(url: str) -> Dict[str, Any]:
    """
    Opens a URL in the default browser.
    """
    clean_url = url.strip()
    if not (clean_url.startswith("http://") or clean_url.startswith("https://")):
        clean_url = "https://" + clean_url

    try:
        webbrowser.open(clean_url, new=2)
        return tool_response(
            success=True,
            message=f"Opened {clean_url} in default browser.",
            data={"url": clean_url}
        )
    except Exception as e:
        return tool_response(
            success=False,
            message=f"Failed to open URL '{url}': {str(e)}"
        )


def search_web(query: str) -> Dict[str, Any]:
    """
    Executes a web search on Google using the default browser.
    """
    query = query.strip()
    if not query:
        return tool_response(success=False, message="Search query cannot be empty.")

    encoded_query = urllib.parse.quote_plus(query)
    search_url = f"https://www.google.com/search?q={encoded_query}"

    try:
        webbrowser.open(search_url, new=2)
        return tool_response(
            success=True,
            message=f"Searching for '{query}'.",
            data={"query": query, "url": search_url}
        )
    except Exception as e:
        return tool_response(
            success=False,
            message=f"Failed to execute search for '{query}': {str(e)}"
        )