"""Tests unitaires pour la génération ICS."""

from __future__ import annotations

import datetime

from icalendar import Calendar

from planning_to_ics.converter import EventData
from planning_to_ics.ics_writer import build_calendar


def _make_event_data(**kwargs: object) -> EventData:
    defaults: dict[str, object] = {
        "summary": "[GI-L2] Théorie des Graphes (CM/TD)",
        "dtstart": datetime.datetime(2026, 2, 10, 8, 0),
        "dtend": datetime.datetime(2026, 2, 10, 12, 0),
        "location": "S-301, ESGC-VAK",
        "description": "Classe: GI-L2\nType: CM/TD\nSalle: S-301",
        "uid": "abcdef1234567890@esgcvak.com",
    }
    defaults.update(kwargs)
    return EventData(**defaults)  # type: ignore[arg-type]


class TestBuildCalendar:
    def test_valid_ical(self) -> None:
        cal = build_calendar([_make_event_data()], revision=0)
        raw = cal.to_ical()
        parsed = Calendar.from_ical(raw)
        assert parsed is not None

    def test_calendar_properties(self) -> None:
        cal = build_calendar([], revision=0)
        raw = cal.to_ical().decode()
        assert "PRODID:-//ESGC-VAK//Planning//FR" in raw
        assert "X-WR-CALNAME:Cours" in raw
        assert "X-WR-TIMEZONE:Africa/Porto-Novo" in raw

    def test_timezone_included(self) -> None:
        cal = build_calendar([], revision=0)
        raw = cal.to_ical().decode()
        assert "BEGIN:VTIMEZONE" in raw
        assert "TZID:Africa/Porto-Novo" in raw
        assert "TZOFFSETFROM:+0100" in raw

    def test_event_count(self) -> None:
        events = [_make_event_data(uid=f"uid{i}@esgcvak.com") for i in range(3)]
        cal = build_calendar(events, revision=0)
        raw = cal.to_ical().decode()
        assert raw.count("BEGIN:VEVENT") == 3

    def test_event_properties(self) -> None:
        cal = build_calendar([_make_event_data()], revision=0)
        raw = cal.to_ical().decode()
        assert "STATUS:CONFIRMED" in raw
        assert "TRANSP:OPAQUE" in raw
        assert "SEQUENCE:0" in raw

    def test_alarms_present(self) -> None:
        cal = build_calendar([_make_event_data()], revision=0)
        raw = cal.to_ical().decode()
        assert raw.count("BEGIN:VALARM") == 3
        assert "TRIGGER:-P2D" in raw
        assert "TRIGGER:-P1D" in raw
        assert "TRIGGER:-PT30M" in raw

    def test_revision_applied(self) -> None:
        cal = build_calendar([_make_event_data()], revision=5)
        raw = cal.to_ical().decode()
        assert "SEQUENCE:5" in raw

    def test_dtstart_with_tzid(self) -> None:
        cal = build_calendar([_make_event_data()], revision=0)
        raw = cal.to_ical().decode()
        assert "DTSTART;TZID=Africa/Porto-Novo:20260210T080000" in raw
