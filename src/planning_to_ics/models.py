"""Structures de données partagées entre les modules."""

from __future__ import annotations

import datetime
from dataclasses import dataclass


@dataclass
class CourseSlot:
    """Représente un créneau de cours extrait du PDF."""

    date: datetime.date
    start_time: datetime.time
    end_time: datetime.time
    course_name: str    # "Théorie des Graphes et Optimisation des Procédés"
    course_type: str    # "CM/TD" (vide si absent)
    class_group: str    # "GI-L2"
    room: str           # "S-301"


@dataclass
class SchedulePeriod:
    """Période couverte par un emploi du temps."""

    start: datetime.date
    end: datetime.date
