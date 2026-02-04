"""
Listuje pliki w katalogu instancji. Pokazuje strukturę projektu.
"""

import os
from pathlib import Path


def run(directory: str = "", _env: dict = None) -> dict:
    """
    Listuje pliki w katalogu instancji.

    Args:
        directory: Podkatalog do listowania (domyślnie root instancji).
                   Np. "site" listuje instances/{id}/site/

    Returns:
        {"files": [...]} lub {"error": "..."}
    """
    instance_dir = os.environ.get('DOJO_INSTANCE_DIR')

    if not instance_dir:
        import sys
        if len(sys.argv) > 1:
            project_root = Path(__file__).parent.parent
            instance_dir = project_root / ".instances" / sys.argv[1]
        else:
            return {"error": "Cannot determine instance directory"}

    instance_path = Path(instance_dir).resolve()
    target = (instance_path / directory).resolve() if directory else instance_path

    # Bezpieczeństwo: nie wychodź poza instancję
    if not str(target).startswith(str(instance_path)):
        return {"error": "Access denied: path outside instance directory"}

    if not target.exists():
        return {"files": [], "note": f"Directory '{directory}' does not exist"}

    if not target.is_dir():
        return {"error": f"Not a directory: {directory}"}

    files = []
    for root, dirs, filenames in os.walk(target):
        # Pomiń .dojo (pliki techniczne)
        dirs[:] = [d for d in dirs if d != '.dojo']
        rel_root = Path(root).relative_to(instance_path)
        for f in filenames:
            rel_path = str(rel_root / f) if str(rel_root) != '.' else f
            files.append(rel_path)

    return {"files": sorted(files)}
