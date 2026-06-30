"""Location normalization — raw strings → ISO-3166 alpha-2 country codes."""
from __future__ import annotations

from typing import Optional

import pycountry


def normalize_country(raw: str) -> Optional[str]:
    """Convert a raw country string to an ISO-3166 alpha-2 code.

    Lookup order: alpha-2, alpha-3, exact name, fuzzy search.
    Returns None if not recognized.
    """
    if not raw:
        return None
    raw = raw.strip()
    if not raw:
        return None

    if len(raw) == 2:
        c = pycountry.countries.get(alpha_2=raw.upper())
        if c:
            return c.alpha_2

    if len(raw) == 3:
        c = pycountry.countries.get(alpha_3=raw.upper())
        if c:
            return c.alpha_2

    c = pycountry.countries.get(name=raw.title())
    if c:
        return c.alpha_2

    try:
        results = pycountry.countries.search_fuzzy(raw)
        return results[0].alpha_2
    except LookupError:
        return None


def parse_location_string(raw: str) -> dict[str, Optional[str]]:
    """Parse a freeform location string into city, region, and country.

    Splits on commas: last part is attempted as country, second-to-last
    as region, first as city.
    """
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    if not parts:
        return {"city": None, "region": None, "country": None}
    if len(parts) == 1:
        return {"city": parts[0], "region": None, "country": None}
    if len(parts) == 2:
        country = normalize_country(parts[1]) or parts[1]
        return {"city": parts[0], "region": None, "country": country}
    country = normalize_country(parts[-1]) or parts[-1]
    return {"city": parts[0], "region": parts[1], "country": country}
