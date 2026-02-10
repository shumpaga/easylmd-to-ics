"""Fixtures pytest partagées."""

from __future__ import annotations

import datetime
from pathlib import Path

import pytest

from planning_to_ics.models import CourseSlot

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_PDF = FIXTURES_DIR / "sample_schedule.pdf"


@pytest.fixture
def sample_pdf() -> Path:
    """Chemin vers le PDF d'exemple."""
    assert SAMPLE_PDF.exists(), f"Fixture manquante : {SAMPLE_PDF}"
    return SAMPLE_PDF


@pytest.fixture
def expected_courses() -> list[CourseSlot]:
    """Les 6 cours attendus du PDF d'exemple."""
    return [
        CourseSlot(
            date=datetime.date(2026, 2, 9),
            start_time=datetime.time(11, 0),
            end_time=datetime.time(15, 0),
            course_name="Introduction à la programmation web: HTML, CSS, JavaScript",
            course_type="CM/TD",
            class_group="GI-L1",
            room="S-304",
        ),
        CourseSlot(
            date=datetime.date(2026, 2, 10),
            start_time=datetime.time(8, 0),
            end_time=datetime.time(12, 0),
            course_name="Théorie des Graphes et Optimisation des Procédés",
            course_type="CM/TD",
            class_group="GI-L2",
            room="S-301",
        ),
        CourseSlot(
            date=datetime.date(2026, 2, 10),
            start_time=datetime.time(14, 0),
            end_time=datetime.time(18, 0),
            course_name="Introduction à la programmation web: HTML, CSS, JavaScript",
            course_type="CM/TD",
            class_group="GI-L1",
            room="S-304",
        ),
        CourseSlot(
            date=datetime.date(2026, 2, 11),
            start_time=datetime.time(15, 0),
            end_time=datetime.time(17, 0),
            course_name="Informatique Fondamentale",
            course_type="CM/TD",
            class_group="GI-L1",
            room="S-304",
        ),
        CourseSlot(
            date=datetime.date(2026, 2, 12),
            start_time=datetime.time(8, 0),
            end_time=datetime.time(12, 0),
            course_name="Théorie des Graphes et Optimisation des Procédés",
            course_type="CM/TD",
            class_group="GI-L2",
            room="S-301",
        ),
        CourseSlot(
            date=datetime.date(2026, 2, 14),
            start_time=datetime.time(11, 0),
            end_time=datetime.time(13, 0),
            course_name="Théorie des Graphes et Optimisation des Procédés",
            course_type="CM/TD",
            class_group="GI-L2",
            room="S-301",
        ),
    ]
