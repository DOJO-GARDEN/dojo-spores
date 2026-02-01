# DOJO Spores

Genomy dla instancji DOJO. Każdy spore definiuje zachowanie, narzędzia i workerów.

## Struktura

```
spores/
├── scout/          Infiltruje web, zbiera dane
├── builder/        Buduje i publikuje artefakty
├── analyst/        Analizuje dane, rekomenduje
└── meta/           Ewoluuje inne spory
```

## Użycie

```bash
# W projekcie z dojo-core
dojo spore pull DOJO-GARDEN/dojo-spores

# Lub w DOJO_SPORES_REPO w .env
DOJO_SPORES_REPO=DOJO-GARDEN/dojo-spores
```

## Tworzenie spore

```
my-spore/
├── manifest.yaml       # wersja, opis, capabilities
├── sensei.yaml         # główny agent (mózg)
├── workers/            # opcjonalne sub-agenty
│   ├── mokuteki.yaml   # strażnik celu
│   ├── metsuke.yaml    # rzecznik
│   └── kensho.yaml     # walidator
└── tools/              # opcjonalne narzędzia Python
    └── my_tool.py
```

## Ewolucja

Mutacje z instancji mogą być promowane do spore:

```python
promote(target_spore="scout")  # z poziomu instancji
```

PR z mutacjami → review → merge → nowa wersja spore.

---

*DOJO-GARDEN*
