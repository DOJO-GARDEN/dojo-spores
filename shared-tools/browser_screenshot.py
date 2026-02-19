"""
Robi screenshot aktualnej strony w przeglądarce.
"""

import json
import uuid
from websocket import create_connection


def run(_env: dict = None) -> dict:
    """
    Robi screenshot aktualnej strony.

    Returns:
        {"screenshot": "data:image/png;base64,..."}
    """
    try:
        ws = create_connection("ws://localhost:8765", timeout=15)
        task_id = str(uuid.uuid4())[:8]

        ws.send(json.dumps({
            "type": "web_command",
            "taskId": task_id,
            "command": "screenshot"
        }))

        response = json.loads(ws.recv())
        ws.close()

        if response.get("status") == "success":
            return response.get("data", {})
        else:
            return {"error": response.get("error", "Unknown error")}

    except Exception as e:
        return {"error": f"Browser not connected: {e}"}
