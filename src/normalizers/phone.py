"""Phone number normalization to E.164 format."""
from __future__ import annotations

from typing import Optional

import phonenumbers
from phonenumbers import NumberParseException


def normalize_phone(raw: str, default_region: str = "US") -> Optional[str]:
    """Normalize a raw phone string to E.164 format.

    Returns None if the input cannot be parsed as a valid phone number.
    """
    try:
        parsed = phonenumbers.parse(raw, default_region)
    except NumberParseException:
        return None
    if not phonenumbers.is_valid_number(parsed):
        return None
    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)


def normalize_phones(raws: list[str], default_region: str = "US") -> list[str]:
    """Normalize a list of raw phone strings, dropping unparseable ones.

    Deduplicates by E.164 value; first occurrence wins.
    """
    normalized = (normalize_phone(r, default_region) for r in raws)
    return list(dict.fromkeys(n for n in normalized if n is not None))
