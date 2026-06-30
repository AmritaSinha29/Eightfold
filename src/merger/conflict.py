"""Conflict resolution policies for field-level merging.

Priority (highest wins): csv > ats_json > linkedin > github > resume > notes
"""
from __future__ import annotations

from enum import IntEnum
from typing import Any


class SourcePriority(IntEnum):
    notes    = 1
    resume   = 2
    linkedin = 3
    github   = 4
    ats_json = 5
    csv      = 6


def pick_winner(values: list[tuple[Any, str]]) -> tuple[Any, str]:
    """Select the winning (value, source_name) pair.

    Policy: unanimous → return first; conflict → highest-priority source wins;
    tie on priority → sort by str(value) for determinism.
    """
    if not values:
        raise ValueError("pick_winner called with empty list")
    if len({v for v, _ in values}) == 1:
        return values[0]
    return sorted(values, key=lambda item: (-_priority(item[1]), str(item[0])))[0]


def merge_lists(items: list[tuple[list, str]]) -> list:
    """Merge list fields from multiple sources, deduplicating in insertion order."""
    flat = [v for lst, _ in items for v in lst]
    return list(dict.fromkeys(flat))


def _priority(source_name: str) -> int:
    return SourcePriority[source_name].value if source_name in SourcePriority.__members__ else 0
