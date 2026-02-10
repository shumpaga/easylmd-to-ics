"""Test d'intégration end-to-end : PDF → ICS."""

from __future__ import annotations

from pathlib import Path

from icalendar import Calendar

from planning_to_ics.converter import convert_slot
from planning_to_ics.extractor import extract_courses
from planning_to_ics.ics_writer import build_calendar, write_ics
from planning_to_ics.models import CourseSlot


class TestEndToEnd:
    def test_full_pipeline(self, sample_pdf: Path, tmp_path: Path) -> None:
        """Pipeline complet : PDF → extraction → conversion → ICS valide."""
        courses, period = extract_courses(sample_pdf)
        events = [convert_slot(c) for c in courses]
        cal = build_calendar(events, revision=0)

        ics_path = tmp_path / "test_output.ics"
        write_ics(cal, ics_path)

        assert ics_path.exists()
        raw = ics_path.read_bytes()
        parsed = Calendar.from_ical(raw)

        vevents = [c for c in parsed.walk() if c.name == "VEVENT"]
        assert len(vevents) == 6

    def test_event_summaries(self, sample_pdf: Path) -> None:
        courses, _ = extract_courses(sample_pdf)
        events = [convert_slot(c) for c in courses]
        cal = build_calendar(events, revision=0)
        raw = cal.to_ical().decode()

        assert "[GI-L1] Introduction" in raw
        assert "[GI-L2]" in raw
        assert "Informatique Fondamentale" in raw

    def test_all_dates_present(self, sample_pdf: Path) -> None:
        courses, _ = extract_courses(sample_pdf)
        events = [convert_slot(c) for c in courses]
        cal = build_calendar(events, revision=0)
        raw = cal.to_ical().decode()

        assert "20260209T" in raw  # Lundi
        assert "20260210T" in raw  # Mardi (2 créneaux)
        assert "20260211T" in raw  # Mercredi
        assert "20260212T" in raw  # Jeudi
        assert "20260214T" in raw  # Samedi

    def test_uid_determinism(self, sample_pdf: Path) -> None:
        """Deux exécutions successives produisent les mêmes UIDs."""
        courses1, _ = extract_courses(sample_pdf)
        courses2, _ = extract_courses(sample_pdf)
        events1 = [convert_slot(c) for c in courses1]
        events2 = [convert_slot(c) for c in courses2]

        uids1 = [e.uid for e in events1]
        uids2 = [e.uid for e in events2]
        assert uids1 == uids2

    def test_all_uids_unique(self, sample_pdf: Path) -> None:
        courses, _ = extract_courses(sample_pdf)
        events = [convert_slot(c) for c in courses]
        uids = [e.uid for e in events]
        assert len(uids) == len(set(uids))

    def test_expected_courses_data(
        self, sample_pdf: Path, expected_courses: list[CourseSlot]
    ) -> None:
        """Vérifie que les données extraites correspondent exactement aux attendues."""
        courses, _ = extract_courses(sample_pdf)
        assert courses == expected_courses
