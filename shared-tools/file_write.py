"""
Zapisuje plik do katalogu instancji. Bezpieczne - nie wychodzi poza katalog instancji.
"""

from pathlib import Path


def run(filename: str, content: str, _env: dict = None) -> dict:
    """
    Zapisuje plik do katalogu instancji.

    Args:
        filename: Nazwa pliku (względna do katalogu instancji)
        content: Zawartość do zapisania

    Returns:
        {"ok": True, "path": "..."} lub {"error": "..."}
    """
    import os
    instance_dir = os.environ.get('DOJO_INSTANCE_DIR')

    if not instance_dir:
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
        # Resolve parent (file może nie istnieć)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path_resolved = file_path.resolve()
        instance_path_resolved = instance_path.resolve()
        if not str(file_path_resolved).startswith(str(instance_path_resolved)):
            return {"error": "Access denied: path outside instance directory"}
    except Exception as e:
        return {"error": f"Invalid path: {str(e)}"}

    # Nie pozwól nadpisywać plików systemowych
    protected = ['.dojo/sensei.yaml', '.dojo/.env']
    rel_path = str(file_path_resolved.relative_to(instance_path_resolved))
    if rel_path in protected:
        return {"error": f"Cannot overwrite protected file: {rel_path}"}

    try:
        file_path.write_text(content, encoding='utf-8')
        return {"ok": True, "path": filename}
    except Exception as e:
        return {"error": f"Failed to write: {str(e)}"}
