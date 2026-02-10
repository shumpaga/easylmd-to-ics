"""Extraction et parsing des emplois du temps PDF EasyLMD via pdfplumber."""

from __future__ import annotations

import datetime
import re
from pathlib import Path

import pdfplumber

from planning_to_ics.models import CourseSlot, SchedulePeriod

DATE_RE = re.compile(r"(\d{2}/\d{2}/\d{4})")
PERIOD_RE = re.compile(r"Période du (\d{2}/\d{2}/\d{4}) au (\d{2}/\d{2}/\d{4})")
TIME_RE = re.compile(r"(\d{2})H(\d{2})\s*-\s*(\d{2})H(\d{2})")
COURSE_TYPE_RE = re.compile(r"\(([^)]+)\)\s*$")


def _parse_date_fr(text: str) -> datetime.date:
    """Parse une date JJ/MM/AAAA en objet date."""
    d, m, y = text.split("/")
    return datetime.date(int(y), int(m), int(d))


def _normalize_text(text: str | None) -> str:
    """Remplace les sauts de ligne par des espaces et nettoie les espaces multiples."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.replace("\n", " ")).strip()


def _extract_date(cell: str | None) -> str | None:
    """Extrait une date JJ/MM/AAAA depuis une cellule Date (peut contenir le nom du jour)."""
    if not cell:
        return None
    m = DATE_RE.search(cell)
    return m.group(1) if m else None


def _parse_time(cell: str) -> tuple[datetime.time, datetime.time] | None:
    """Parse '11H00 - 15H00' en tuple (start_time, end_time)."""
    m = TIME_RE.search(cell)
    if not m:
        return None
    return (
        datetime.time(int(m.group(1)), int(m.group(2))),
        datetime.time(int(m.group(3)), int(m.group(4))),
    )


def _parse_course_name(raw: str) -> tuple[str, str]:
    """Sépare le nom du cours et le type entre parenthèses.

    Returns:
        (nom_du_cours, type) — type est vide si absent.
    """
    m = COURSE_TYPE_RE.search(raw)
    if m:
        return raw[: m.start()].strip(), m.group(1)
    return raw, ""


def _extract_period(pdf: pdfplumber.PDF) -> SchedulePeriod | None:
    """Extrait la période 'du JJ/MM/AAAA au JJ/MM/AAAA' depuis le texte du PDF."""
    for page in pdf.pages:
        text = page.extract_text() or ""
        m = PERIOD_RE.search(text)
        if m:
            return SchedulePeriod(
                start=_parse_date_fr(m.group(1)),
                end=_parse_date_fr(m.group(2)),
            )
    return None


def extract_courses(pdf_path: str | Path) -> tuple[list[CourseSlot], SchedulePeriod | None]:
    """Extrait tous les créneaux de cours du PDF.

    Gère les cellules fusionnées (propagation de la dernière date non-vide),
    le texte multi-lignes, et les tableaux multi-pages.

    Returns:
        (liste_de_cours, période) — période est None si non trouvée dans le PDF.
    """
    pdf_path = Path(pdf_path)
    courses: list[CourseSlot] = []

    with pdfplumber.open(pdf_path) as pdf:
        period = _extract_period(pdf)
        last_date_str: str | None = None

        for page in pdf.pages:
            for table in page.extract_tables():
                for row in table:
                    if not row or len(row) < 5:
                        continue

                    # Ignorer l'en-tête
                    if row[0] and row[0].strip().lower() == "date":
                        continue

                    # Extraire ou propager la date (cellules fusionnées)
                    date_str = _extract_date(row[0])
                    if date_str:
                        last_date_str = date_str
                    else:
                        date_str = last_date_str

                    if not date_str:
                        continue

                    # Parser l'horaire
                    horaire = _normalize_text(row[1])
                    if not horaire:
                        continue
                    times = _parse_time(horaire)
                    if not times:
                        continue

                    # Parser le cours
                    cours_raw = _normalize_text(row[2])
                    if not cours_raw:
                        continue
                    course_name, course_type = _parse_course_name(cours_raw)

                    class_group = _normalize_text(row[3])
                    room = _normalize_text(row[4])

                    if not class_group:
                        continue

                    courses.append(
                        CourseSlot(
                            date=_parse_date_fr(date_str),
                            start_time=times[0],
                            end_time=times[1],
                            course_name=course_name,
                            course_type=course_type,
                            class_group=class_group,
                            room=room,
                        )
                    )

    # Fallback : déduire la période des dates min/max si non trouvée dans le PDF
    if period is None and courses:
        dates = [c.date for c in courses]
        period = SchedulePeriod(start=min(dates), end=max(dates))

    return courses, period
