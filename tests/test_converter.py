"""Tests unitaires pour la conversion CourseSlot → EventData."""

from __future__ import annotations

import datetime

from planning_to_ics.converter import (
    compute_uid,
    convert_slot,
    format_description,
    format_location,
    format_summary,
)
from planning_to_ics.models import CourseSlot


def _make_slot(**kwargs: object) -> CourseSlot:
    defaults: dict[str, object] = {
        "date": datetime.date(2026, 2, 10),
        "start_time": datetime.time(8, 0),
        "end_time": datetime.time(12, 0),
        "course_name": "Théorie des Graphes et Optimisation des Procédés",
        "course_type": "CM/TD",
        "class_group": "GI-L2",
        "room": "S-301",
    }
    defaults.update(kwargs)
    return CourseSlot(**defaults)  # type: ignore[arg-type]


class TestFormatSummary:
    def test_with_type(self) -> None:
        slot = _make_slot()
        assert format_summary(slot) == (
            "[GI-L2] Théorie des Graphes et Optimisation des Procédés (CM/TD)"
        )

    def test_without_type(self) -> None:
        slot = _make_slot(course_type="")
        assert format_summary(slot) == (
            "[GI-L2] Théorie des Graphes et Optimisation des Procédés"
        )


class TestFormatLocation:
    def test_format(self) -> None:
        assert format_location(_make_slot()) == "S-301, ESGC-VAK"


class TestFormatDescription:
    def test_format(self) -> None:
        desc = format_description(_make_slot())
        assert "Classe: GI-L2" in desc
        assert "Type: CM/TD" in desc
        assert "Salle: S-301" in desc


class TestComputeUid:
    def test_deterministic(self) -> None:
        slot = _make_slot()
        assert compute_uid(slot) == compute_uid(slot)

    def test_different_for_different_slots(self) -> None:
        slot1 = _make_slot(date=datetime.date(2026, 2, 10))
        slot2 = _make_slot(date=datetime.date(2026, 2, 11))
        assert compute_uid(slot1) != compute_uid(slot2)

    def test_format(self) -> None:
        uid = compute_uid(_make_slot())
        assert uid.endswith("@esgcvak.com")
        assert len(uid.split("@")[0]) == 16


class TestConvertSlot:
    def test_dtstart_dtend(self) -> None:
        event = convert_slot(_make_slot())
        assert event.dtstart == datetime.datetime(2026, 2, 10, 8, 0)
        assert event.dtend == datetime.datetime(2026, 2, 10, 12, 0)

    def test_all_fields_populated(self) -> None:
        event = convert_slot(_make_slot())
        assert event.summary
        assert event.location
        assert event.description
        assert event.uid
