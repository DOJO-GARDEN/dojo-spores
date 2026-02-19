"""
Otwiera URL w przeglądarce Chrome (przez DOJO Chrome Extension).
Zwraca tytuł strony i HTML.
"""

import json
import uuid
from websocket import create_connection


def run(url: str, _env: dict = None) -> dict:
    """
    Otwiera stronę w przeglądarce.

    Args:
        url: URL do otwarcia

    Returns:
        {"url": "...", "title": "...", "html": "..."}
    """
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    try:
        ws = create_connection("ws://localhost:8765", timeout=10)
        task_id = str(uuid.uuid4())[:8]

        ws.send(json.dumps({
            "type": "web_command",
            "taskId": task_id,
            "command": "fetch",
            "url": url
        }))

        response = json.loads(ws.recv())
        ws.close()

        if response.get("status") == "success":
            data = response.get("data", {})
            html = data.get("html", "")
            if len(html) > 15000:
                html = html[:15000] + "..."
            return {"url": data.get("url", url), "title": data.get("title", ""), "html": html}
        else:
            return {"error": response.get("error", "Unknown error")}

    except Exception as e:
        return {"error": f"Browser not connected: {e}"}
