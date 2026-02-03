"""
Weryfikacja dla repo-builder spore.

Typy weryfikacji ewoluują wraz ze spore.
Core ładuje funkcje verify_*() dynamicznie.
"""

import requests


def verify_http(v: dict) -> dict:
    """
    Sprawdź czy URL zwraca oczekiwany status HTTP.

    Parametry w GOAL.md:
        - type: http
          target: https://example.com/
          expect: 200
    """
    target = v.get('target')
    expect = v.get('expect', 200)

    if not target:
        return {'ok': False, 'error': 'missing target URL'}

    try:
        expect = int(expect)
    except (ValueError, TypeError):
        return {'ok': False, 'error': f'expect must be integer, got: {expect}'}

    try:
        r = requests.get(target, timeout=30, allow_redirects=True)

        if r.status_code == expect:
            return {
                'ok': True,
                'status': r.status_code,
                'target': target
            }
        else:
            return {
                'ok': False,
                'status': r.status_code,
                'expected': expect,
                'target': target,
                'error': f'expected {expect}, got {r.status_code}'
            }
    except requests.Timeout:
        return {'ok': False, 'error': f'timeout connecting to {target}'}
    except requests.ConnectionError as e:
        return {'ok': False, 'error': f'connection failed: {e}'}
    except Exception as e:
        return {'ok': False, 'error': str(e)}


def verify_file(v: dict) -> dict:
    """
    Sprawdź czy plik istnieje w repo (via GitHub API).

    Parametry w GOAL.md:
        - type: file
          repo: username/repo-name
          path: index.html
    """
    import os

    repo = v.get('repo')
    path = v.get('path')

    if not repo or not path:
        return {'ok': False, 'error': 'missing repo or path'}

    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        return {'ok': False, 'error': 'missing GITHUB_TOKEN'}

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        url = f"https://api.github.com/repos/{repo}/contents/{path}"
        r = requests.get(url, headers=headers, timeout=30)

        if r.status_code == 200:
            return {
                'ok': True,
                'repo': repo,
                'path': path,
                'size': r.json().get('size')
            }
        elif r.status_code == 404:
            return {
                'ok': False,
                'error': f'file not found: {repo}/{path}'
            }
        else:
            return {
                'ok': False,
                'error': f'GitHub API error: {r.status_code}'
            }
    except Exception as e:
        return {'ok': False, 'error': str(e)}
