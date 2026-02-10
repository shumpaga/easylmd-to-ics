"""Tests unitaires pour l'extraction PDF."""

from __future__ import annotations

import datetime
from pathlib import Path

from planning_to_ics.extractor import extract_courses
from planning_to_ics.models import CourseSlot


class TestExtractCourses:
    def test_extract_count(self, sample_pdf: Path) -> None:
        courses, period = extract_courses(sample_pdf)
        assert len(courses) == 6

    def test_period_extracted(self, sample_pdf: Path) -> None:
        _, period = extract_courses(sample_pdf)
        assert period is not None
        assert period.start == datetime.date(2026, 2, 9)
        assert period.end == datetime.date(2026, 2, 28)

    def test_all_courses_match(
        self, sample_pdf: Path, expected_courses: list[CourseSlot]
    ) -> None:
        courses, _ = extract_courses(sample_pdf)
        assert courses == expected_courses

    def test_merged_cell_propagation(self, sample_pdf: Path) -> None:
        """Mardi 10/02 a 2 créneaux — la date doit être propagée."""
        courses, _ = extract_courses(sample_pdf)
        tuesday_courses = [c for c in courses if c.date == datetime.date(2026, 2, 10)]
        assert len(tuesday_courses) == 2
        assert tuesday_courses[0].start_time == datetime.time(8, 0)
        assert tuesday_courses[1].start_time == datetime.time(14, 0)

    def test_multiline_course_name(self, sample_pdf: Path) -> None:
        """Les noms de cours multi-lignes sont normalisés en une seule ligne."""
        courses, _ = extract_courses(sample_pdf)
        assert courses[0].course_name == (
            "Introduction à la programmation web: HTML, CSS, JavaScript"
        )

    def test_course_type_parsed(self, sample_pdf: Path) -> None:
        courses, _ = extract_courses(sample_pdf)
        for c in courses:
            assert c.course_type == "CM/TD"
