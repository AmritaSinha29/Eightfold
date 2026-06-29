"""Conflict resolution policies for field-level merging.

When multiple sources provide different values for the same field, the
conflict resolver picks a winner based on a priority ordering. The ordering
reflects how structured and reliable each source type is.

Priority (highest wins):
  csv > ats_json > linkedin > github > resume > notes

Tie-breaking between equal-priority sources is alphabetical by value,
ensuring determinism even when the source order varies.
"""
from __future__ import annotations

from enum import IntEnum
from typing import Any


class SourcePriority(IntEnum):
    """Numeric priority for each source type. Higher value = higher priority."""

    notes = 1
    resume = 2
    linkedin = 3
    github = 4
    ats_json = 5
    csv = 6


def pick_winner(values: list[tuple[Any, str]]) -> tuple[Any, str]:
    """Select the winning (value, source_name) pair from a set of candidates.

    Resolution policy:
      1. If all values are equal: return the first one (unanimous).
      2. If conflicting: return the value from the highest-priority source.
      3. Tie on priority: sort by str(value) for determinism.

    Args:
        values: Non-empty list of (value, source_name) tuples.

    Returns:
        The winning (value, source_name) pair.

    Raises:
        ValueError: If values is empty.
    """
    # TODO: If not values: raise ValueError("pick_winner called with empty list")
    # TODO: If all value entries are equal: return values[0]
    # TODO: sorted_values = sorted(values, key=lambda v: (-_priority(v[1]), str(v[0])))
    # TODO: return sorted_values[0]
    raise NotImplementedError


def merge_lists(items: list[tuple[list, str]]) -> list:
    """Merge list-typed fields (emails, phones, other_links) from multiple sources.

    Combines all lists and deduplicates, preserving first-occurrence order.

    Args:
        items: List of (list_value, source_name) pairs from different sources.

    Returns:
        Flat deduplicated list.
    """
    # TODO: Flatten: [v for lst, _ in items for v in lst]
    # TODO: Deduplicate preserving order: list(dict.fromkeys(flat))
    raise NotImplementedError


def _priority(source_name: str) -> int:
    """Return the numeric priority for a source name.

    Unknown source names get priority 0 (lowest).

    Args:
        source_name: Source identifier string, e.g. "csv", "github".
    """
    # TODO: return SourcePriority[source_name].value if source_name in SourcePriority.__members__ else 0
    raise NotImplementedError
