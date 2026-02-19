"""
Zwraca interaktywne elementy na stronie (Accessibility Tree).
Użyj do zorientowania się co można kliknąć/wpisać.
"""

import json
import uuid
from websocket import create_connection


def run(_env: dict = None) -> dict:
    """
    Pobiera listę interaktywnych elementów z aktualnej strony.

    Returns:
        {"elements": [{"id": ..., "role": "button", "name": "Submit"}, ...]}
    """
    try:
        ws = create_connection("ws://localhost:8765", timeout=10)
        task_id = str(uuid.uuid4())[:8]

        ws.send(json.dumps({
            "type": "web_command",
            "taskId": task_id,
            "command": "explore"
        }))

        response = json.loads(ws.recv())
        ws.close()

        if response.get("status") == "success":
            return response.get("data", {})
        else:
            return {"error": response.get("error", "Unknown error")}

    except Exception as e:
        return {"error": f"Browser not connected: {e}"}
