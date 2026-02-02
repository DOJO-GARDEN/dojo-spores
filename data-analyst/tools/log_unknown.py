"""
Zamyka pętlę wiedzy instancji.

Dwa tryby:
- Z answer → zapisuje fakt do knowledge.json (uczenie się)
- Bez answer → loguje pytanie do unknown_questions.json (luka w wiedzy)

Kensho wywołuje z answer po udanej walidacji.
Kensho wywołuje bez answer gdy baza nie ma odpowiedzi.

Pliki są PER-INSTANCE (nie per-spore).
"""
import json
import os
from pathlib import Path
from datetime import datetime

def _get_instance_dir():
    instance_dir = os.environ.get('DOJO_INSTANCE_DIR')
    if instance_dir:
        return Path(instance_dir)
    # Fallback dla testów lokalnych
    return Path(__file__).parent.parent

def run(question: str, answer: str = None):
    instance_dir = _get_instance_dir()
    knowledge_file = instance_dir / "knowledge.json"
    unknown_file = instance_dir / "unknown_questions.json"

    # Tryb uczenia: zapisz zweryfikowany fakt do bazy wiedzy
    if answer:
        knowledge = []
        if knowledge_file.exists():
            try:
                knowledge = json.loads(knowledge_file.read_text())
            except:
                pass

        # Nie duplikuj — nadpisz jeśli pytanie już istnieje
        for entry in knowledge:
            if entry.get("q", "").lower() == question.lower():
                entry["a"] = answer
                break
        else:
            knowledge.append({"q": question, "a": answer})

        knowledge_file.write_text(json.dumps(knowledge, indent=2, ensure_ascii=False))
        return {"saved": True, "path": str(knowledge_file)}

    # Tryb luki: loguj pytanie bez odpowiedzi
    questions = []
    if unknown_file.exists():
        try:
            questions = json.loads(unknown_file.read_text())
        except:
            pass

    if question not in [q.get("q") for q in questions]:
        questions.append({
            "q": question,
            "timestamp": datetime.now().isoformat()
        })
        unknown_file.write_text(json.dumps(questions, indent=2, ensure_ascii=False))

    return {"logged": True, "path": str(unknown_file)}
