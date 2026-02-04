"""
Google Sheets API tool dla DOJO.
Używa tego samego tokenu co google_drive (scope rozszerzony).
"""

import os
import json
from pathlib import Path


def _get_credentials():
    """Pobiera credentials (wspólne z google_drive)."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    project_root = Path(__file__).parent.parent
    token_path = project_root / ".dojo" / "gdrive_token.json"

    if not token_path.exists():
        return None, "No token. Run: ./dojo auth"

    creds = Credentials.from_authorized_user_file(str(token_path))

    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            token_path.write_text(creds.to_json())
        else:
            return None, "Token expired. Run: ./dojo auth"

    return creds, None


def _get_service():
    """Zwraca Google Sheets service."""
    from googleapiclient.discovery import build
    creds, err = _get_credentials()
    if err:
        raise RuntimeError(err)
    return build('sheets', 'v4', credentials=creds)


def _get_drive_service():
    """Zwraca Google Drive service (do tworzenia arkuszy)."""
    from googleapiclient.discovery import build
    creds, err = _get_credentials()
    if err:
        raise RuntimeError(err)
    return build('drive', 'v3', credentials=creds)


def run(action: str, spreadsheet_id: str = "", sheet: str = "Sheet1", range: str = "", values: str = "", title: str = "", _env: dict = None) -> dict:
    """
    Operacje na Google Sheets.

    Args:
        action:
            - "create" - utwórz nowy arkusz (title = nazwa)
            - "read" - czytaj dane (spreadsheet_id, range np. "A1:C10")
            - "append" - dodaj wiersz (spreadsheet_id, values jako JSON array)
            - "write" - zapisz dane (spreadsheet_id, range, values jako JSON 2D array)
            - "list" - listuj arkusze w spreadsheet
            - "find" - znajdź arkusz po nazwie (title)
        spreadsheet_id: ID arkusza (z URL)
        sheet: nazwa zakładki (domyślnie Sheet1)
        range: zakres komórek (np. "A1:C10", "A:A")
        values: dane jako JSON string (array dla append, 2D array dla write)
        title: nazwa arkusza (dla create/find)

    Returns:
        dict z wynikiem
    """
    try:
        if action == "create":
            if not title:
                return {"error": "Missing title"}

            drive = _get_drive_service()
            file_metadata = {
                'name': title,
                'mimeType': 'application/vnd.google-apps.spreadsheet'
            }
            file = drive.files().create(body=file_metadata, fields='id, webViewLink').execute()
            return {
                "ok": True,
                "spreadsheet_id": file['id'],
                "url": file.get('webViewLink'),
                "title": title
            }

        elif action == "find":
            if not title:
                return {"error": "Missing title"}

            drive = _get_drive_service()
            q = f"name='{title}' and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false"
            results = drive.files().list(q=q, fields="files(id, name, webViewLink)").execute()
            files = results.get('files', [])

            if not files:
                return {"found": False, "title": title}

            return {
                "found": True,
                "spreadsheet_id": files[0]['id'],
                "url": files[0].get('webViewLink'),
                "title": files[0]['name']
            }

        elif action == "read":
            if not spreadsheet_id:
                return {"error": "Missing spreadsheet_id"}

            service = _get_service()
            range_str = f"{sheet}!{range}" if range else sheet

            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_str
            ).execute()

            rows = result.get('values', [])
            return {"rows": rows, "count": len(rows)}

        elif action == "append":
            if not spreadsheet_id:
                return {"error": "Missing spreadsheet_id"}
            if not values:
                return {"error": "Missing values"}

            service = _get_service()
            data = json.loads(values) if isinstance(values, str) else values

            # Jeśli to pojedynczy wiersz (1D array), opakuj w 2D
            if data and not isinstance(data[0], list):
                data = [data]

            result = service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet}!A:A",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": data}
            ).execute()

            return {
                "ok": True,
                "updated_range": result.get('updates', {}).get('updatedRange'),
                "rows_added": result.get('updates', {}).get('updatedRows', 0)
            }

        elif action == "write":
            if not spreadsheet_id:
                return {"error": "Missing spreadsheet_id"}
            if not range:
                return {"error": "Missing range"}
            if not values:
                return {"error": "Missing values"}

            service = _get_service()
            data = json.loads(values) if isinstance(values, str) else values

            result = service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=f"{sheet}!{range}",
                valueInputOption="USER_ENTERED",
                body={"values": data}
            ).execute()

            return {
                "ok": True,
                "updated_range": result.get('updatedRange'),
                "updated_cells": result.get('updatedCells', 0)
            }

        elif action == "list":
            if not spreadsheet_id:
                return {"error": "Missing spreadsheet_id"}

            service = _get_service()
            result = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()

            sheets = [s['properties']['title'] for s in result.get('sheets', [])]
            return {"sheets": sheets, "title": result.get('properties', {}).get('title')}

        else:
            return {"error": f"Unknown action: {action}. Use: create, read, append, write, list, find"}

    except Exception as e:
        return {"error": str(e)}
