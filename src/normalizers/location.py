"""Location normalization — raw strings → ISO-3166 alpha-2 country codes.

Uses the pycountry library for country lookup. Fuzzy search is used as
a fallback so that "United States", "USA", "us", and "US" all resolve
to "US".
"""
from __future__ import annotations

from typing import Optional


def normalize_country(raw: str) -> Optional[str]:
    """Convert a raw country string to an ISO-3166 alpha-2 code.

    Lookup order:
    1. Direct alpha-2 match (len == 2)
    2. Direct alpha-3 match (len == 3)
    3. Exact name match
    4. Fuzzy search (pycountry.countries.search_fuzzy)

    Args:
        raw: Country name or code in any form, e.g. "United States", "USA",
             "us", "India", "IN".

    Returns:
        ISO-3166 alpha-2 string (e.g. "US", "IN"); None if not recognized.

    Examples:
        >>> normalize_country("United States")
        'US'
        >>> normalize_country("india")
        'IN'
        >>> normalize_country("unknownland")
        None
    """
    # TODO: raw = raw.strip()
    # TODO: if len(raw) == 2: try pycountry.countries.get(alpha_2=raw.upper())
    # TODO: if len(raw) == 3: try pycountry.countries.get(alpha_3=raw.upper())
    # TODO: try pycountry.countries.get(name=raw.title())
    # TODO: try pycountry.countries.search_fuzzy(raw)[0]
    # TODO: Catch LookupError from search_fuzzy → return None
    raise NotImplementedError


def parse_location_string(raw: str) -> dict[str, Optional[str]]:
    """Parse a freeform location string into city, region, and country.

    Heuristic: split on commas; last segment is attempted as country,
    second-to-last as region, first as city.

    Args:
        raw: Location string in any format, e.g. "San Francisco, CA, US",
             "London, UK", "Bangalore", "San Francisco Bay Area".

    Returns:
        Dict with keys "city", "region", "country" (all Optional[str]).
        country is normalized to ISO-3166 alpha-2 if recognized; otherwise
        the raw token is stored and normalization is deferred.
    """
    # TODO: parts = [p.strip() for p in raw.split(",")]
    # TODO: If one part: treat as city only
    # TODO: If two parts: city, country (try normalize_country on last)
    # TODO: If three+ parts: city, region, country
    # TODO: Return {"city": ..., "region": ..., "country": ...}
    raise NotImplementedError
