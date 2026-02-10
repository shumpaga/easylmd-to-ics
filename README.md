# planning-to-ics

Convertit les emplois du temps PDF EasyLMD (ESGC-VAK) en fichiers `.ics` importables dans Apple Calendar.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install pdfplumber icalendar
pip install pytest ruff  # pour le développement
```

## Usage

```bash
python planning.py emploi_du_temps.pdf

# Options
python planning.py emploi_du_temps.pdf --output-dir ~/Desktop
python planning.py emploi_du_temps.pdf --revision 1      # mise à jour d'un import précédent
python planning.py emploi_du_temps.pdf --dry-run          # aperçu sans générer de fichier
python planning.py emploi_du_temps.pdf --verbose          # détails de parsing
```

### Workflow typique

1. Recevoir le PDF d'emploi du temps par email
2. Le sauvegarder dans `data/pdfs/`
3. Lancer `python planning.py data/pdfs/emploi_du_temps.pdf`
4. Double-cliquer sur le `.ics` généré dans `output/` pour l'importer dans Apple Calendar

Le fichier ICS généré utilise des UIDs déterministes : réimporter un `.ics` pour la même période met à jour les événements existants au lieu de créer des doublons.

## Structure du projet

```
planning-to-ics/
├── planning.py                  # Point d'entrée
├── src/planning_to_ics/
│   ├── models.py                # Dataclasses (CourseSlot, SchedulePeriod)
│   ├── extractor.py             # PDF → list[CourseSlot] (pdfplumber)
│   ├── converter.py             # CourseSlot → EventData (formatage ICS)
│   ├── ics_writer.py            # EventData → fichier .ics (icalendar)
│   └── cli.py                   # Parsing args, orchestration, affichage
├── tests/
│   ├── fixtures/                # PDF d'exemple pour les tests
│   ├── test_extractor.py
│   ├── test_converter.py
│   ├── test_ics_writer.py
│   └── test_integration.py
├── data/pdfs/                   # PDFs source (gitignored)
└── output/                      # Fichiers .ics générés (gitignored)
```

## Développement

```bash
# Lancer les tests
pytest

# Lancer les tests avec détails
pytest -v

# Linter
ruff check src/ tests/
```
