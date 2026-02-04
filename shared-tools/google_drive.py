"""
Google Drive API tool dla instancji DOJO.
Wymaga GOOGLE_CLIENT_ID i GOOGLE_CLIENT_SECRET w .env
"""

import os
import json
from pathlib import Path

# Zakresy dostępu (Drive + Sheets + Gmail)
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
]


def _get_project_root() -> Path:
    """Zwraca główny katalog projektu DOJO."""
    return Path(__file__).parent.parent


def _get_credentials():
    """Pobiera lub odświeża credentials OAuth2."""
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    project_root = _get_project_root()
    token_path = project_root / ".dojo" / "gdrive_token.json"

    creds = None

    # Wczytaj istniejący token
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    # Odśwież lub uzyskaj nowy token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Potrzebna autoryzacja - zwróć URL
            client_id = os.environ.get('GOOGLE_CLIENT_ID')
            client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')

            if not client_id or not client_secret:
                raise RuntimeError("Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET in .env")

            client_config = {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost:5173/"]
                }
            }

            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=5173, open_browser=True)

        # Zapisz token
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(creds.to_json())

    return creds


def _get_service():
    """Zwraca Google Drive service."""
    from googleapiclient.discovery import build
    creds = _get_credentials()
    return build('drive', 'v3', credentials=creds)


def _find_or_create_folder(service, folder_name: str, parent_id: str = None) -> str:
    """Znajdź folder po nazwie lub utwórz. Zwraca folder_id."""
    # Szukaj istniejącego
    q = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        q += f" and '{parent_id}' in parents"

    results = service.files().list(q=q, fields="files(id)").execute()
    files = results.get('files', [])

    if files:
        return files[0]['id']

    # Utwórz nowy
    metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_id:
        metadata['parents'] = [parent_id]

    folder = service.files().create(body=metadata, fields='id').execute()
    return folder['id']


def run(action: str, path: str = "", content: str = "", folder_id: str = "", query: str = "", _env: dict = None) -> dict:
    """
    Operacje na Google Drive.

    Args:
        action: Akcja do wykonania:
            - "list" - listuj pliki (opcjonalnie w folderze folder_id lub z query)
            - "download" - pobierz plik (path = file_id)
            - "upload" - wyślij plik (path = nazwa, content = zawartość, folder_id = opcjonalny)
            - "mkdir" - utwórz folder (path = nazwa, folder_id = rodzic)
            - "search" - szukaj plików (query = zapytanie Drive)
            - "auth_url" - zwróć URL do autoryzacji (jeśli brak tokenu)
        path: Ścieżka/nazwa pliku lub file_id (zależnie od akcji)
        content: Zawartość pliku (dla upload)
        folder_id: ID folderu (opcjonalne)
        query: Zapytanie wyszukiwania (dla search)

    Returns:
        dict z wynikiem lub {"error": "..."}
    """
    try:
        if action == "auth_url":
            # Sprawdź czy mamy token
            project_root = _get_project_root()
            token_path = project_root / ".dojo" / "gdrive_token.json"
            if token_path.exists():
                return {"status": "authorized", "message": "Token exists"}

            client_id = os.environ.get('GOOGLE_CLIENT_ID')
            if not client_id:
                return {"error": "Missing GOOGLE_CLIENT_ID"}

            auth_url = (
                f"https://accounts.google.com/o/oauth2/auth?"
                f"client_id={client_id}&"
                f"redirect_uri=http://localhost:8080/&"
                f"scope=https://www.googleapis.com/auth/drive&"
                f"response_type=code&"
                f"access_type=offline"
            )
            return {"status": "needs_auth", "auth_url": auth_url}

        elif action == "list":
            service = _get_service()
            q = query if query else None
            if folder_id and not query:
                q = f"'{folder_id}' in parents"

            results = service.files().list(
                q=q,
                pageSize=100,
                fields="files(id, name, mimeType, size, modifiedTime)"
            ).execute()

            files = results.get('files', [])
            return {"files": files, "count": len(files)}

        elif action == "search":
            if not query:
                return {"error": "Missing query parameter"}
            service = _get_service()
            results = service.files().list(
                q=query,
                pageSize=50,
                fields="files(id, name, mimeType, size, modifiedTime)"
            ).execute()
            files = results.get('files', [])
            return {"files": files, "count": len(files)}

        elif action == "download":
            if not path:
                return {"error": "Missing path (file_id)"}
            service = _get_service()

            # Pobierz metadane
            file_meta = service.files().get(fileId=path, fields="name, mimeType").execute()

            # Pobierz zawartość
            from googleapiclient.http import MediaIoBaseDownload
            import io

            # Dla Google Docs eksportuj jako tekst
            mime = file_meta.get('mimeType', '')
            if mime.startswith('application/vnd.google-apps'):
                if 'document' in mime:
                    export_mime = 'text/plain'
                elif 'spreadsheet' in mime:
                    export_mime = 'text/csv'
                else:
                    export_mime = 'text/plain'
                request = service.files().export_media(fileId=path, mimeType=export_mime)
            else:
                request = service.files().get_media(fileId=path)

            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

            content = fh.getvalue()
            try:
                content = content.decode('utf-8')
            except:
                import base64
                content = base64.b64encode(content).decode('utf-8')
                return {"name": file_meta['name'], "content": content, "encoding": "base64"}

            return {"name": file_meta['name'], "content": content}

        elif action == "upload":
            if not path:
                return {"error": "Missing path (filename)"}
            if not content:
                return {"error": "Missing content"}

            service = _get_service()
            from googleapiclient.http import MediaInMemoryUpload

            # Obsługa ścieżek: "folder/plik.json" lub "folder/subfolder/plik.json"
            target_folder_id = folder_id
            filename = path

            if "/" in path:
                parts = path.split("/")
                filename = parts[-1]
                folders = parts[:-1]

                # Utwórz/znajdź zagnieżdżone foldery
                current_parent = None
                for folder_name in folders:
                    current_parent = _find_or_create_folder(service, folder_name, current_parent)
                target_folder_id = current_parent

            file_metadata = {'name': filename}
            if target_folder_id:
                file_metadata['parents'] = [target_folder_id]

            media = MediaInMemoryUpload(content.encode('utf-8'), mimetype='text/plain')

            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()

            return {"id": file['id'], "name": file['name'], "link": file.get('webViewLink'), "folder": "/".join(path.split("/")[:-1]) if "/" in path else "root"}

        elif action == "mkdir":
            if not path:
                return {"error": "Missing path (folder name)"}

            service = _get_service()
            file_metadata = {
                'name': path,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if folder_id:
                file_metadata['parents'] = [folder_id]

            folder = service.files().create(
                body=file_metadata,
                fields='id, name, webViewLink'
            ).execute()

            return {"id": folder['id'], "name": folder['name'], "link": folder.get('webViewLink')}

        else:
            return {"error": f"Unknown action: {action}. Use: list, download, upload, mkdir, search, auth_url"}

    except Exception as e:
        return {"error": str(e)}
