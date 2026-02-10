"""Interface CLI : parsing des arguments, orchestration, affichage console."""

from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

from planning_to_ics.converter import convert_slot
from planning_to_ics.extractor import extract_courses
from planning_to_ics.ics_writer import CALNAME, build_calendar, write_ics
from planning_to_ics.models import CourseSlot, SchedulePeriod

DAYS_FR = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]


def _day_abbr(date: datetime.date) -> str:
    return DAYS_FR[date.weekday()]


def _summary_short(slot: CourseSlot, max_name: int = 25) -> str:
    """Version courte du nom de cours pour l'affichage console."""
    name = slot.course_name
    if len(name) > max_name:
        name = name[: max_name - 1].rstrip() + "."
    typ = f" ({slot.course_type})" if slot.course_type else ""
    return f"[{slot.class_group}] {name}{typ}"


def _ics_filename(period: SchedulePeriod | None) -> str:
    """Génère le nom du fichier ICS : esgcvak_{debut}_{fin}.ics."""
    if period:
        return f"esgcvak_{period.start.isoformat()}_{period.end.isoformat()}.ics"
    return "esgcvak_planning.ics"


def _print_summary(
    courses: list[CourseSlot],
    period: SchedulePeriod | None,
    pdf_name: str,
    ics_path: Path,
    revision: int,
    dry_run: bool = False,
) -> None:
    """Affiche le résumé des cours trouvés."""
    print(f"\n📄 Lecture de {pdf_name}...")

    if period:
        start = period.start.strftime("%d/%m/%Y")
        end = period.end.strftime("%d/%m/%Y")
        print(f"📅 {len(courses)} cours trouvés pour la période du {start} au {end}")
    else:
        print(f"📅 {len(courses)} cours trouvés")

    print()
    for c in courses:
        abbr = _day_abbr(c.date)
        dm = c.date.strftime("%d/%m")
        start = c.start_time.strftime("%H:%M")
        end = c.end_time.strftime("%H:%M")
        print(f"  {abbr} {dm}  {start}-{end}  {_summary_short(c)}")

    if dry_run:
        print("\n🔍 Mode dry-run : aucun fichier généré.")
    else:
        print(f"\n✅ Fichier généré : {ics_path}")
        print("   Rappels : 2 jours, 1 jour, 30 min avant chaque cours")
        print(f"   Calendrier cible : {CALNAME}")
        print(f"   Révision : {revision}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convertit un emploi du temps PDF EasyLMD en fichier ICS.",
    )
    parser.add_argument("pdf", help="Chemin vers le fichier PDF EasyLMD")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Répertoire de sortie (défaut: ./output/)",
    )
    parser.add_argument(
        "--revision",
        type=int,
        default=0,
        help="Numéro de séquence pour les mises à jour (défaut: 0)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Affiche les cours extraits sans générer le .ics",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Affiche les détails de parsing (debug)",
    )
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"❌ Fichier introuvable : {pdf_path}", file=sys.stderr)
        sys.exit(1)

    try:
        courses, period = extract_courses(pdf_path)
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du PDF : {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)

    if not courses:
        print("❌ Aucun cours trouvé dans le PDF.", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print(f"[debug] {len(courses)} créneaux extraits")
        for c in courses:
            print(f"  {c}")

    ics_path = args.output_dir / _ics_filename(period)

    if not args.dry_run:
        events = [convert_slot(c) for c in courses]
        cal = build_calendar(events, args.revision)
        write_ics(cal, ics_path)

    _print_summary(courses, period, pdf_path.name, ics_path, args.revision, args.dry_run)


if __name__ == "__main__":
    main()
