"""Transforme les CourseSlot extraits en données formatées pour la génération ICS."""

from __future__ import annotations

import datetime
import hashlib
from dataclasses import dataclass

from planning_to_ics.models import CourseSlot

LOCATION_SUFFIX = "ESGC-VAK"


@dataclass
class EventData:
    """Données formatées prêtes pour la génération ICS."""

    summary: str
    dtstart: datetime.datetime
    dtend: datetime.datetime
    location: str
    description: str
    uid: str


def compute_uid(slot: CourseSlot) -> str:
    """Génère un UID déterministe et stable pour un créneau de cours.

    Le même créneau produit toujours le même UID, permettant à Apple Calendar
    de mettre à jour un événement existant au lieu de créer un doublon.
    """
    date_iso = slot.date.isoformat()
    start = slot.start_time.strftime("%H:%M")
    end = slot.end_time.strftime("%H:%M")
    raw = f"{date_iso}|{start}|{end}|{slot.course_name}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16] + "@esgcvak.com"


def format_summary(slot: CourseSlot) -> str:
    """Compose le SUMMARY : [Classe] Nom du cours (Type)."""
    if slot.course_type:
        return f"[{slot.class_group}] {slot.course_name} ({slot.course_type})"
    return f"[{slot.class_group}] {slot.course_name}"


def format_location(slot: CourseSlot) -> str:
    """Compose le LOCATION : Salle, ESGC-VAK."""
    return f"{slot.room}, {LOCATION_SUFFIX}"


def format_description(slot: CourseSlot) -> str:
    """Compose le DESCRIPTION avec les infos complémentaires."""
    return f"Classe: {slot.class_group}\nType: {slot.course_type}\nSalle: {slot.room}"


def convert_slot(slot: CourseSlot) -> EventData:
    """Convertit un CourseSlot en EventData prêt pour l'écriture ICS."""
    return EventData(
        summary=format_summary(slot),
        dtstart=datetime.datetime.combine(slot.date, slot.start_time),
        dtend=datetime.datetime.combine(slot.date, slot.end_time),
        location=format_location(slot),
        description=format_description(slot),
        uid=compute_uid(slot),
    )
