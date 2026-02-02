"""
Sprawdza bazę wiedzy instancji.
Zwraca odpowiedź lub null jeśli nie znaleziono.

Baza wiedzy jest PER-INSTANCE (nie per-spore).
"""
import json
import os
from pathlib import Path

def _get_knowledge_path():
    instance_dir = os.environ.get('DOJO_INSTANCE_DIR')
    if instance_dir:
        return Path(instance_dir) / "knowledge.json"
    # Fallback dla testów lokalnych
    return Path(__file__).parent.parent / "knowledge.json"

def run(question: str):
    knowledge_file = _get_knowledge_path()
    if not knowledge_file.exists():
        return {"answer": None}

    knowledge = json.loads(knowledge_file.read_text())

    # Proste wyszukiwanie po kluczach
    question_lower = question.lower()
    for entry in knowledge:
        if entry.get("q", "").lower() in question_lower or question_lower in entry.get("q", "").lower():
            return {"answer": entry.get("a")}

    return {"answer": None}
