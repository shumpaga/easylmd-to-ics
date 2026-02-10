"""Génération de fichiers ICS à partir de données d'événements."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from icalendar import Alarm, Calendar, Event, Timezone, TimezoneStandard

from planning_to_ics.converter import EventData

TIMEZONE_ID = "Africa/Porto-Novo"
PRODID = "-//ESGC-VAK//Planning//FR"
CALNAME = "Cours"


def _build_timezone() -> Timezone:
    """Construit le composant VTIMEZONE pour Africa/Porto-Novo (UTC+1 fixe)."""
    tz = Timezone()
    tz.add("TZID", TIMEZONE_ID)

    std = TimezoneStandard()
    std.add("DTSTART", datetime(1970, 1, 1, 0, 0, 0))
    std.add("TZOFFSETFROM", timedelta(hours=1))
    std.add("TZOFFSETTO", timedelta(hours=1))
    std.add("TZNAME", "WAT")
    tz.add_component(std)

    return tz


def _build_alarms() -> list[Alarm]:
    """Construit les 3 rappels : 2 jours, 1 jour, 30 min avant."""
    alarms = []
    for td, desc in [
        (timedelta(days=-2), "Cours dans 2 jours"),
        (timedelta(days=-1), "Cours demain"),
        (timedelta(minutes=-30), "Cours dans 30 minutes"),
    ]:
        alarm = Alarm()
        alarm.add("ACTION", "DISPLAY")
        alarm.add("DESCRIPTION", desc)
        alarm.add("TRIGGER", td)
        alarms.append(alarm)
    return alarms


def _build_event(event_data: EventData, revision: int, dtstamp: datetime) -> Event:
    """Construit un VEVENT à partir d'un EventData."""
    event = Event()
    event.add("SUMMARY", event_data.summary)
    event.add("DTSTART", event_data.dtstart, parameters={"TZID": TIMEZONE_ID})
    event.add("DTEND", event_data.dtend, parameters={"TZID": TIMEZONE_ID})
    event.add("LOCATION", event_data.location)
    event.add("DESCRIPTION", event_data.description)
    event.add("UID", event_data.uid)
    event.add("SEQUENCE", revision)
    event.add("STATUS", "CONFIRMED")
    event.add("TRANSP", "OPAQUE")
    event.add("DTSTAMP", dtstamp)

    for alarm in _build_alarms():
        event.add_component(alarm)

    return event


def build_calendar(events: list[EventData], revision: int) -> Calendar:
    """Construit le calendrier ICS complet."""
    cal = Calendar()
    cal.add("VERSION", "2.0")
    cal.add("PRODID", PRODID)
    cal.add("CALSCALE", "GREGORIAN")
    cal.add("METHOD", "PUBLISH")
    cal.add("X-WR-CALNAME", CALNAME)
    cal.add("X-WR-TIMEZONE", TIMEZONE_ID)

    cal.add_component(_build_timezone())

    dtstamp = datetime.now(timezone.utc)
    for event_data in events:
        cal.add_component(_build_event(event_data, revision, dtstamp))

    return cal


def write_ics(calendar: Calendar, output_path: Path) -> None:
    """Écrit le calendrier ICS dans un fichier."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(calendar.to_ical())
