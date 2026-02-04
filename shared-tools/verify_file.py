"""
Sprawdza czy plik istnieje (lokalnie lub w GitHub repo).

GOAL.md (lokalny):
    verify:
      - type: file
        path: output/results.json

GOAL.md (GitHub):
    verify:
      - type: file
        repo: username/repo-name
        path: index.html
"""

import os
import urllib.request
import urllib.error
import json
from pathlib import Path


def run(path: str, repo: str = "", contains: str = "", _env: dict = None) -> dict:
    """
    Weryfikuje istnienie pliku.

    Args:
        path: Ścieżka do pliku (lokalna lub w repo)
        repo: GitHub repo w formacie "user/repo" (opcjonalne)
        contains: Tekst który plik musi zawierać (opcjonalne)

    Returns:
        {"ok": True/False, ...}
    """
    if not path:
        return {'ok': False, 'error': 'missing path'}

    # GitHub
    if repo:
        return _verify_github(repo, path, _env)

    # Lokalny plik
    return _verify_local(path, contains)


def _verify_local(path: str, contains: str = "") -> dict:
    """Sprawdź plik lokalny w katalogu instancji."""
    instance_dir = os.environ.get('DOJO_INSTANCE_DIR', '.')
    file_path = Path(instance_dir) / path

    if not file_path.exists():
        return {
            'ok': False,
            'path': path,
            'error': f'file not found: {path}'
        }

    result = {
        'ok': True,
        'path': path,
        'size': file_path.stat().st_size
    }

    # Sprawdź zawartość
    if contains:
        try:
            content = file_path.read_text()
            if contains not in content:
                return {
                    'ok': False,
                    'path': path,
                    'error': f'file does not contain: {contains}'
                }
            result['contains'] = contains
        except Exception as e:
            return {'ok': False, 'path': path, 'error': f'cannot read file: {e}'}

    return result


def _verify_github(repo: str, path: str, _env: dict = None) -> dict:
    """Sprawdź plik w GitHub repo."""
    _env = _env or {}
    token = _env.get('GITHUB_TOKEN') or os.environ.get('GITHUB_TOKEN')

    if not token:
        return {'ok': False, 'error': 'missing GITHUB_TOKEN'}

    url = f"https://api.github.com/repos/{repo}/contents/{path}"

    req = urllib.request.Request(url, headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "DOJO-Verify/1.0"
    })

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
            return {
                'ok': True,
                'repo': repo,
                'path': path,
                'size': data.get('size')
            }

    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {'ok': False, 'error': f'file not found: {repo}/{path}'}
        return {'ok': False, 'error': f'GitHub API error: {e.code}'}
    except Exception as e:
        return {'ok': False, 'error': str(e)}
