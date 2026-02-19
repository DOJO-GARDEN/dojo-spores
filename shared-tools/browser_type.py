"""
Wpisuje tekst w element na stronie. Podaj name/role lub backendDOMNodeId z browser_explore.
"""

import json
import uuid
from websocket import create_connection


def run(text: str, name: str = "", role: str = "", backendDOMNodeId: str = "", _env: dict = None) -> dict:
    """
    Wpisuje tekst w element.

    Args:
        text: Tekst do wpisania
        name: Tekst/label elementu
        role: Rola: textbox, searchbox...
        backendDOMNodeId: ID z browser_explore

    Returns:
        {"typed": ...} lub {"error": "..."}
    """
    params = {"text": text}
    if name:
        params["name"] = name
    if role:
        params["role"] = role
    if backendDOMNodeId:
        try:
            params["backendDOMNodeId"] = int(backendDOMNodeId)
        except ValueError:
            return {"error": "backendDOMNodeId must be a number"}

    try:
        ws = create_connection("ws://localhost:8765", timeout=30)
        task_id = str(uuid.uuid4())[:8]

        ws.send(json.dumps({
            "type": "web_command",
            "taskId": task_id,
            "command": "type",
            **params
        }))

        response = json.loads(ws.recv())
        ws.close()

        if response.get("status") == "success":
            return {"ok": True, **response.get("data", {})}
        else:
            return {"error": response.get("error", "Unknown error")}

    except Exception as e:
        return {"error": f"Browser not connected: {e}"}
