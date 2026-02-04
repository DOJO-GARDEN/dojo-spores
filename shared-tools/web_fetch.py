"""
Pobiera zawartość strony internetowej. Zwraca tekst (bez HTML).
"""

import urllib.request
import re
from html.parser import HTMLParser


class TextExtractor(HTMLParser):
    """Wyciąga tekst z HTML, pomijając skrypty i style."""

    def __init__(self):
        super().__init__()
        self.text = []
        self.skip = False
        self.skip_tags = {'script', 'style', 'noscript', 'header', 'footer', 'nav'}

    def handle_starttag(self, tag, attrs):
        if tag in self.skip_tags:
            self.skip = True

    def handle_endtag(self, tag):
        if tag in self.skip_tags:
            self.skip = False

    def handle_data(self, data):
        if not self.skip:
            text = data.strip()
            if text:
                self.text.append(text)

    def get_text(self):
        return '\n'.join(self.text)


def run(url: str, max_length: int = 10000) -> dict:
    """
    Pobiera stronę i zwraca tekst.

    Args:
        url: URL strony do pobrania
        max_length: Maksymalna długość tekstu (domyślnie 10000)

    Returns:
        {"content": "...", "url": "...", "title": "..."}
    """
    try:
        max_length = int(max_length)
    except (ValueError, TypeError):
        max_length = 10000

    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        return {"error": f"Failed to fetch: {str(e)}"}

    # Wyciągnij tytuł
    title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
    title = title_match.group(1).strip() if title_match else ""

    # Wyciągnij tekst
    extractor = TextExtractor()
    try:
        extractor.feed(html)
        content = extractor.get_text()
    except Exception:
        # Fallback: usuń wszystkie tagi
        content = re.sub(r'<[^>]+>', ' ', html)
        content = re.sub(r'\s+', ' ', content).strip()

    # Ogranicz długość
    if len(content) > max_length:
        content = content[:max_length] + "..."

    return {
        "url": url,
        "title": title,
        "content": content
    }
