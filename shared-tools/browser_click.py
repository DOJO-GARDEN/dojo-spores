"""
Klika element na stronie. Podaj name (tekst) i/lub role, albo backendDOMNodeId z browser_explore.
"""

import json
import uuid
from websocket import create_connection


def run(name: str = "", role: str = "", backendDOMNodeId: str = "", _env: dict = None) -> dict:
    """
    Klika element na stronie.

    Args:
        name: Tekst elementu (szuka częściowo)
        role: Rola: button, link, textbox...
        backendDOMNodeId: ID z browser_explore (najdokładniejsze)

    Returns:
        {"clicked": ...} lub {"error": "..."}
    """
    params = {}
    if name:
        params["name"] = name
    if role:
        params["role"] = role
    if backendDOMNodeId:
        try:
            params["backendDOMNodeId"] = int(backendDOMNodeId)
        except ValueError:
            return {"error": "backendDOMNodeId must be a number"}

    if not params:
        return {"error": "Podaj name, role lub backendDOMNodeId"}

    try:
        ws = create_connection("ws://localhost:8765", timeout=30)
        task_id = str(uuid.uuid4())[:8]

        ws.send(json.dumps({
            "type": "web_command",
            "taskId": task_id,
            "command": "click",
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
