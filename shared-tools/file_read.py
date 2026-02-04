"""
Czyta plik z katalogu instancji. Bezpieczne - nie wychodzi poza katalog instancji.
"""

from pathlib import Path


def run(filename: str, _env: dict = None) -> dict:
    """
    Czyta plik z katalogu instancji.

    Args:
        filename: Nazwa pliku (względna do katalogu instancji)

    Returns:
        {"content": "..."} lub {"error": "..."}
    """
    # Znajdź katalog instancji (tools są w .dojo/tools lub native)
    # _env jest przekazywane przez mcp_server, ale potrzebujemy ścieżki instancji
    # Użyjemy zmiennej środowiskowej lub obliczymy z __file__

    import os
    instance_dir = os.environ.get('DOJO_INSTANCE_DIR')

    if not instance_dir:
        # Fallback: jeśli uruchomione z mcp_server, path jest w sys.argv
        import sys
        if len(sys.argv) > 1:
            project_root = Path(__file__).parent.parent
            instance_dir = project_root / ".instances" / sys.argv[1]
        else:
            return {"error": "Cannot determine instance directory"}

    instance_path = Path(instance_dir)
    file_path = instance_path / filename

    # Bezpieczeństwo: sprawdź czy ścieżka nie wychodzi poza instancję
    try:
        file_path = file_path.resolve()
        instance_path = instance_path.resolve()
        if not str(file_path).startswith(str(instance_path)):
            return {"error": "Access denied: path outside instance directory"}
    except Exception:
        return {"error": "Invalid path"}

    if not file_path.exists():
        return {"error": f"File not found: {filename}"}

    if not file_path.is_file():
        return {"error": f"Not a file: {filename}"}

    try:
        content = file_path.read_text(encoding='utf-8')
        return {"content": content, "path": filename}
    except Exception as e:
        return {"error": f"Failed to read: {str(e)}"}
