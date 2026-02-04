"""
Wyszukuje w internecie przez DuckDuckGo. Zwraca listę wyników.
"""

import urllib.request
import urllib.parse
import json
import re


def run(query: str, max_results: int = 5) -> dict:
    """
    Wyszukuje w DuckDuckGo.

    Args:
        query: Zapytanie wyszukiwania
        max_results: Maksymalna liczba wyników (domyślnie 5)

    Returns:
        {"results": [{"title": ..., "url": ..., "snippet": ...}, ...]}
    """
    try:
        max_results = int(max_results)
    except (ValueError, TypeError):
        max_results = 5

    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

    results = []

    # Parse DuckDuckGo HTML results
    # Szukamy linków z klasą result__a
    pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
    matches = re.findall(pattern, html)

    # Szukamy snippetów
    snippet_pattern = r'<a[^>]*class="result__snippet"[^>]*>([^<]*(?:<[^>]*>[^<]*)*)</a>'
    snippets = re.findall(snippet_pattern, html)

    for i, (href, title) in enumerate(matches[:max_results]):
        # DuckDuckGo używa redirect URL, wyciągamy prawdziwy URL
        if 'uddg=' in href:
            real_url = urllib.parse.unquote(href.split('uddg=')[1].split('&')[0])
        else:
            real_url = href

        snippet = ""
        if i < len(snippets):
            # Usuń tagi HTML ze snippetu
            snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()

        results.append({
            "title": title.strip(),
            "url": real_url,
            "snippet": snippet
        })

    return {"results": results}
