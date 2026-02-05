# DOJO Spores

Genomy dla organizmów DOJO. Każdy spore definiuje brain, organy i narzędzia.

## Dostępne spore

| Spore | Opis |
|-------|------|
| `ping-pong` | Test komunikacji między organami |
| `web-scout` | Infiltruje web, zbiera dane |
| `entrepreneur` | Szuka klientów, składa oferty |
| `data-analyst` | Analizuje dane |
| `page-lander` | Buduje landing page |
| `repo-builder` | Buduje repozytoria |
| `spore-evolver` | Ewoluuje inne spory |

## Struktura spore

```
my-spore/
├── manifest.yaml       # wersja, opis
├── brain.yaml          # główny agent (koordynator)
├── organs/             # sub-agenci (SKILL.md)
│   └── worker/
│       └── SKILL.md
└── tools/              # narzędzia Python
    └── my_tool.py
```

## Format brain.yaml

```yaml
description: Opis co robi brain
model: haiku          # haiku | sonnet | opus
max_turns: 5

prompt: |
  Instrukcje dla braina...
```

## Format SKILL.md (organ)

```markdown
---
name: worker
description: Opis organu
dojo:
  model: haiku
  max_turns: 3
---

Instrukcje dla organu...
```

## Shared tools

Wspólne narzędzia w `shared-tools/`:

- `verify_http.py` — weryfikacja HTTP
- `verify_file.py` — weryfikacja plików
- `web_fetch.py` — pobieranie stron
- `web_search.py` — wyszukiwanie
- `file_read.py`, `file_write.py`, `file_list.py`
- `gmail.py`, `google_drive.py`, `google_sheets.py`

## Użycie

```bash
# Kiełkowanie organizmu ze spore
curl -X POST http://localhost:8000/seed \
  -H "Content-Type: application/json" \
  -d '{
    "organisms": {
      "test": {
        "spore": "ping-pong",
        "goal": "Test komunikacji"
      }
    }
  }'
```

## Ewolucja

Organizm może tworzyć nowe organy i tools w runtime. Udane mutacje wracają do spore przez `promote()`.

---

*DOJO-GARDEN*
