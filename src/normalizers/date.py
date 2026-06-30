"""Date normalization to YYYY-MM format and years-of-experience computation."""
from __future__ import annotations

from datetime import date
from typing import Optional

import dateparser


OPEN_ENDED_TOKENS = frozenset({"present", "current", "now", "ongoing", "today", "–", "-"})


def normalize_date(raw: str) -> Optional[str]:
    """Parse a raw date string and return it in YYYY-MM format.

    Returns None for open-ended tokens (Present, Current) or unparseable input.
    """
    if not raw:
        return None
    stripped = raw.strip()
    if stripped.lower() in OPEN_ENDED_TOKENS:
        return None
    parsed = dateparser.parse(
        stripped,
        settings={"PREFER_DAY_OF_MONTH": "first", "RETURN_AS_TIMEZONE_AWARE": False},
    )
    if parsed is None:
        return None
    return parsed.strftime("%Y-%m")


def compute_years_experience(experiences: list[dict]) -> Optional[float]:
    """Compute total years of experience, deduplicating overlapping intervals.

    Each dict must have "start" and "end" keys (YYYY-MM strings).
    end=None means a current role; today's date is used as the end.
    """
    today = date.today()
    intervals: list[tuple[int, int]] = []

    for exp in experiences:
        start_str = exp.get("start")
        end_str = exp.get("end")
        if not start_str:
            continue
        try:
            sy, sm = map(int, start_str.split("-"))
        except (ValueError, AttributeError):
            continue
        if end_str:
            try:
                ey, em = map(int, end_str.split("-"))
            except (ValueError, AttributeError):
                ey, em = today.year, today.month
        else:
            ey, em = today.year, today.month
        start_mo = sy * 12 + sm
        end_mo = ey * 12 + em
        if end_mo > start_mo:
            intervals.append((start_mo, end_mo))

    if not intervals:
        return None

    intervals.sort()
    merged = [list(intervals[0])]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])

    total_months = sum(end - start for start, end in merged)
    return round(total_months / 12.0, 1)
