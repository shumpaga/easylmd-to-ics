#!/usr/bin/env python3
"""Convertit un emploi du temps PDF EasyLMD en fichier ICS pour Apple Calendar.

Usage: python planning.py <fichier.pdf> [options]
"""

import sys
from pathlib import Path

# Ajouter src/ au path pour les imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from planning_to_ics.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
