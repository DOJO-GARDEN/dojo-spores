"""
Deploy HTML do GitHub Pages.
Wymaga GITHUB_TOKEN, GITHUB_USERNAME w .env

Zwraca _verify field - scheduler automatycznie dodaje do kolejki weryfikacji.
"""

import os
import base64

def run(action: str, repo: str = "", path: str = "", content: str = "", message: str = "Update via DOJO", _env: dict = None) -> dict:
    """
    Operacje na GitHub repo (dla Pages).

    Args:
        action: "deploy" | "list" | "read" | "delete"
        repo: nazwa repo (np. "moj-landing")
        path: ścieżka pliku w repo (np. "index.html")
        content: zawartość pliku (dla deploy)
        message: commit message

    Returns:
        dict z wynikiem + _verify dla automatycznej weryfikacji
    """
    import httpx

    token = (_env or {}).get('GITHUB_TOKEN') or os.environ.get('GITHUB_TOKEN')
    username = (_env or {}).get('GITHUB_USERNAME') or os.environ.get('GITHUB_USERNAME')

    if not token or not username:
        return {"error": "Missing GITHUB_TOKEN or GITHUB_USERNAME in .env"}

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    if not repo:
        repo = f"{username}.github.io"

    full_repo = f"{username}/{repo}" if "/" not in repo else repo
    api_base = f"https://api.github.com/repos/{full_repo}"

    try:
        if action == "deploy":
            if not path:
                return {"error": "Missing path"}
            if not content:
                return {"error": "Missing content"}

            with httpx.Client(timeout=30) as client:
                # Sprawdź czy repo istnieje, jeśli nie - utwórz
                r = client.get(api_base, headers=headers)
                if r.status_code == 404:
                    create_r = client.post(
                        "https://api.github.com/user/repos",
                        headers=headers,
                        json={"name": repo.split("/")[-1], "auto_init": True}
                    )
                    if create_r.status_code not in (200, 201):
                        return {"error": f"Cannot create repo: {create_r.text}"}

                # Pobierz domyślną gałąź
                repo_info = client.get(api_base, headers=headers)
                default_branch = "main"
                if repo_info.status_code == 200:
                    default_branch = repo_info.json().get("default_branch", "main")

                # Włącz GitHub Pages
                pages_r = client.post(
                    f"{api_base}/pages",
                    headers={**headers, "Accept": "application/vnd.github+json"},
                    json={"build_type": "legacy", "source": {"branch": default_branch, "path": "/"}}
                )
                if pages_r.status_code in (409, 422):
                    client.put(
                        f"{api_base}/pages",
                        headers={**headers, "Accept": "application/vnd.github+json"},
                        json={"build_type": "legacy", "source": {"branch": default_branch, "path": "/"}}
                    )

                # Sprawdź czy plik istnieje (potrzebujemy SHA do update)
                file_url = f"{api_base}/contents/{path}"
                file_r = client.get(file_url, headers=headers)
                sha = file_r.json().get("sha") if file_r.status_code == 200 else None

                # Utwórz/zaktualizuj plik
                payload = {
                    "message": message,
                    "content": base64.b64encode(content.encode()).decode()
                }
                if sha:
                    payload["sha"] = sha

                put_r = client.put(file_url, headers=headers, json=payload)
                if put_r.status_code not in (200, 201):
                    return {"error": f"Deploy failed: {put_r.text}"}

                pages_url = f"https://{username}.github.io/{repo.split('/')[-1]}/{path}"
                if path == "index.html":
                    pages_url = f"https://{username}.github.io/{repo.split('/')[-1]}/"

                return {
                    "ok": True,
                    "url": pages_url,
                    "repo": full_repo,
                    "path": path
                }

        elif action == "list":
            with httpx.Client(timeout=30) as client:
                r = client.get(f"{api_base}/contents/{path or ''}", headers=headers)
                if r.status_code == 200:
                    data = r.json()
                    if isinstance(data, list):
                        return {"files": [f["name"] for f in data], "count": len(data)}
                    return {"file": data["name"], "size": data.get("size")}
                return {"error": f"List failed: {r.status_code}"}

        elif action == "read":
            if not path:
                return {"error": "Missing path"}
            with httpx.Client(timeout=30) as client:
                r = client.get(f"{api_base}/contents/{path}", headers=headers)
                if r.status_code == 200:
                    data = r.json()
                    content = base64.b64decode(data["content"]).decode()
                    return {"name": data["name"], "content": content}
                return {"error": f"Read failed: {r.status_code}"}

        elif action == "delete":
            if not path:
                return {"error": "Missing path"}
            with httpx.Client(timeout=30) as client:
                file_r = client.get(f"{api_base}/contents/{path}", headers=headers)
                if file_r.status_code != 200:
                    return {"error": "File not found"}
                sha = file_r.json()["sha"]

                del_r = client.request(
                    "DELETE",
                    f"{api_base}/contents/{path}",
                    headers=headers,
                    json={"message": message, "sha": sha}
                )
                if del_r.status_code == 200:
                    return {"ok": True, "deleted": path}
                return {"error": f"Delete failed: {del_r.text}"}

        else:
            return {"error": f"Unknown action: {action}. Use: deploy, list, read, delete"}

    except Exception as e:
        return {"error": str(e)}
