"""Phone number normalization to E.164 format.

Uses the phonenumbers library (Google's libphonenumber port) for parsing
and validation. Unparseable or invalid numbers are returned as None rather
than raising — the pipeline never invents a value.
"""
from __future__ import annotations

from typing import Optional


def normalize_phone(raw: str, default_region: str = "US") -> Optional[str]:
    """Normalize a raw phone string to E.164 format.

    Args:
        raw: Raw phone string in any format, e.g. "(555) 123-4567",
             "+91-9999999999", "650.555.0202".
        default_region: ISO-3166 alpha-2 region code assumed when the input
                        has no country code. Defaults to "US".

    Returns:
        E.164 string (e.g. "+15551234567") on success; None if the input
        cannot be parsed as a valid phone number.

    Examples:
        >>> normalize_phone("(555) 123-4567")
        '+15551234567'
        >>> normalize_phone("+91 99999 99999", default_region="IN")
        '+919999999999'
        >>> normalize_phone("not-a-phone")
        None
    """
    # TODO: import phonenumbers
    # TODO: parsed = phonenumbers.parse(raw, default_region)  — wrap in try/except NumberParseException
    # TODO: if not phonenumbers.is_valid_number(parsed): return None
    # TODO: return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    raise NotImplementedError


def normalize_phones(
    raws: list[str],
    default_region: str = "US",
) -> list[str]:
    """Normalize a list of raw phone strings, dropping unparseable ones.

    Deduplicates by the resulting E.164 value (so "(555) 123-4567" and
    "5551234567" in the same list collapse to one entry).

    Args:
        raws: List of raw phone strings.
        default_region: Default region for numbers without a country code.

    Returns:
        Deduplicated list of E.164 strings. Order: first occurrence wins.
    """
    # TODO: [normalize_phone(r, default_region) for r in raws]
    # TODO: Filter out None
    # TODO: Deduplicate preserving order (use dict.fromkeys trick)
    raise NotImplementedError
