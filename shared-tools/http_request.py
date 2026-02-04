"""
Wykonuje zapytania HTTP do zewnętrznych API. Obsługuje GET, POST, PUT, DELETE.
"""

import urllib.request
import urllib.parse
import json


def run(url: str, method: str = "GET", body: str = None, headers: str = None, _env: dict = None) -> dict:
    """
    Wykonuje zapytanie HTTP.

    Args:
        url: URL do wywołania
        method: Metoda HTTP (GET, POST, PUT, DELETE)
        body: Body zapytania (dla POST/PUT) - JSON string
        headers: Nagłówki jako JSON string, np. '{"Authorization": "Bearer xxx"}'

    Returns:
        {"status": 200, "body": "...", "headers": {...}}
    """
    method = method.upper()
    if method not in ('GET', 'POST', 'PUT', 'DELETE', 'PATCH'):
        return {"error": f"Unsupported method: {method}"}

    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    # Parse headers
    req_headers = {
        "User-Agent": "DOJO-Agent/1.0",
        "Accept": "application/json"
    }

    if headers:
        try:
            custom_headers = json.loads(headers)
            req_headers.update(custom_headers)
        except json.JSONDecodeError:
            return {"error": "Invalid headers JSON"}

    # Przygotuj body
    data = None
    if body and method in ('POST', 'PUT', 'PATCH'):
        try:
            # Sprawdź czy to valid JSON
            json.loads(body)
            data = body.encode('utf-8')
            req_headers["Content-Type"] = "application/json"
        except json.JSONDecodeError:
            # Nie JSON - wyślij jako form
            data = body.encode('utf-8')

    req = urllib.request.Request(url, data=data, headers=req_headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            status = response.status
            resp_headers = dict(response.headers)
            resp_body = response.read().decode('utf-8', errors='ignore')

            # Spróbuj sparsować jako JSON
            try:
                resp_body = json.loads(resp_body)
            except json.JSONDecodeError:
                pass

            return {
                "status": status,
                "body": resp_body,
                "headers": resp_headers
            }
    except urllib.error.HTTPError as e:
        return {
            "status": e.code,
            "error": str(e.reason),
            "body": e.read().decode('utf-8', errors='ignore') if e.fp else None
        }
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}
