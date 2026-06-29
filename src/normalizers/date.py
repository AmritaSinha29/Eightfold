"""Date normalization to YYYY-MM format and years-of-experience computation.

Uses the dateparser library for flexible multi-format parsing. The PREFER_DAY_OF_MONTH
setting is used so that a month-year input always resolves to the first of the month,
making the output deterministic.
"""
from __future__ import annotations

from typing import Optional


# Strings that represent an open-ended / current role end date.
OPEN_ENDED_TOKENS = frozenset({"present", "current", "now", "ongoing", "today", "–"})


def normalize_date(raw: str) -> Optional[str]:
    """Parse a raw date string and return it in YYYY-MM format.

    Handles common formats: "March 2021", "03/2021", "2021-03-15",
    "Jan 2020", "2020" (year-only → January assumed), "Present" → None.

    Args:
        raw: Raw date string from any source.

    Returns:
        "YYYY-MM" string on success; None for open-ended dates or if the
        input cannot be parsed.

    Examples:
        >>> normalize_date("March 2021")
        '2021-03'
        >>> normalize_date("Present")
        None
        >>> normalize_date("2021")
        '2021-01'
        >>> normalize_date("garbage")
        None
    """
    # TODO: Strip and check raw.lower() against OPEN_ENDED_TOKENS → return None
    # TODO: import dateparser
    # TODO: parsed = dateparser.parse(raw, settings={"PREFER_DAY_OF_MONTH": "first", "RETURN_AS_TIMEZONE_AWARE": False})
    # TODO: If parsed is None: return None
    # TODO: return parsed.strftime("%Y-%m")
    raise NotImplementedError


def compute_years_experience(
    experiences: list[dict],
) -> Optional[float]:
    """Compute total years of experience from a list of normalized experience dicts.

    Handles overlapping date ranges by computing the union of all intervals
    before summing, so concurrent roles are not double-counted.

    Args:
        experiences: List of dicts with "start" and "end" keys (YYYY-MM strings).
                     "end" == None means a current role (uses today's date).

    Returns:
        Total years as a float rounded to one decimal place; None if no valid
        date ranges were found.

    Example:
        experiences = [
            {"start": "2020-01", "end": "2022-06"},
            {"start": "2021-06", "end": None},   # current
        ]
        → union spans 2020-01 to today → computed total
    """
    # TODO: Parse each "YYYY-MM" to (year, month) int tuple
    # TODO: Replace None end with (today.year, today.month)
    # TODO: Drop entries where start parse fails
    # TODO: Sort intervals by start
    # TODO: Merge overlapping/adjacent intervals (standard sweep-line algorithm)
    # TODO: Sum total months across merged intervals
    # TODO: return round(total_months / 12.0, 1)
    raise NotImplementedError
