"""
Sprawdza czy URL zwraca oczekiwany status HTTP.

GOAL.md:
    verify:
      - type: http
        target: https://example.com/
        expect: 200
"""

import urllib.request
import urllib.error


def run(target: str, expect: int = 200, _env: dict = None) -> dict:
    """
    Weryfikuje dostępność URL.

    Args:
        target: URL do sprawdzenia
        expect: Oczekiwany status HTTP (domyślnie 200)

    Returns:
        {"ok": True/False, "status": int, ...}
    """
    if not target:
        return {'ok': False, 'error': 'missing target URL'}

    try:
        expect = int(expect)
    except (ValueError, TypeError):
        return {'ok': False, 'error': f'expect must be integer, got: {expect}'}

    try:
        req = urllib.request.Request(
            target,
            headers={"User-Agent": "DOJO-Verify/1.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            status = response.getcode()

            if status == expect:
                return {
                    'ok': True,
                    'status': status,
                    'target': target
                }
            else:
                return {
                    'ok': False,
                    'status': status,
                    'expected': expect,
                    'target': target,
                    'error': f'expected {expect}, got {status}'
                }

    except urllib.error.HTTPError as e:
        if e.code == expect:
            return {'ok': True, 'status': e.code, 'target': target}
        return {
            'ok': False,
            'status': e.code,
            'expected': expect,
            'target': target,
            'error': f'expected {expect}, got {e.code}'
        }
    except urllib.error.URLError as e:
        return {'ok': False, 'error': f'connection failed: {e.reason}'}
    except TimeoutError:
        return {'ok': False, 'error': f'timeout connecting to {target}'}
    except Exception as e:
        return {'ok': False, 'error': str(e)}
