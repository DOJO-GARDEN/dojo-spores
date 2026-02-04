"""
Gmail API tool dla DOJO.
Wymaga scope gmail w OAuth (./dojo auth ponownie po dodaniu).
"""

import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
    """Zwraca Gmail service."""
    from googleapiclient.discovery import build
    creds, err = _get_credentials()
    if err:
        raise RuntimeError(err)
    return build('gmail', 'v1', credentials=creds)


def run(action: str, to: str = "", subject: str = "", body: str = "", html: bool = False, _env: dict = None) -> dict:
    """
    Operacje Gmail.

    Args:
        action:
            - "send" - wyślij email (to, subject, body)
            - "me" - informacje o koncie
        to: adres email odbiorcy (lub lista oddzielona przecinkami)
        subject: temat
        body: treść (text lub HTML jeśli html=True)
        html: czy body to HTML (domyślnie False)

    Returns:
        dict z wynikiem
    """
    try:
        service = _get_service()

        if action == "me":
            profile = service.users().getProfile(userId='me').execute()
            return {
                "email": profile.get('emailAddress'),
                "messages_total": profile.get('messagesTotal'),
                "threads_total": profile.get('threadsTotal')
            }

        elif action == "send":
            if not to:
                return {"error": "Missing 'to' address"}
            if not subject:
                return {"error": "Missing 'subject'"}
            if not body:
                return {"error": "Missing 'body'"}

            # Utwórz wiadomość
            if html:
                message = MIMEMultipart('alternative')
                message['to'] = to
                message['subject'] = subject
                part = MIMEText(body, 'html')
                message.attach(part)
            else:
                message = MIMEText(body)
                message['to'] = to
                message['subject'] = subject

            # Encode
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # Wyślij
            result = service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()

            return {
                "ok": True,
                "message_id": result.get('id'),
                "to": to,
                "subject": subject
            }

        else:
            return {"error": f"Unknown action: {action}. Use: send, me"}

    except Exception as e:
        error_str = str(e)
        if "insufficient" in error_str.lower() or "scope" in error_str.lower():
            return {"error": "Gmail scope not authorized. Delete .dojo/gdrive_token.json and run: ./dojo auth"}
        return {"error": error_str}
