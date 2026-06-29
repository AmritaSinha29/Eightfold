"""Tests for all normalizer functions.

Tests are stubs — they document expected behavior and will be filled in
during implementation. Skipped tests still enumerate the contract.
"""
from __future__ import annotations

import pytest

from src.normalizers.date import compute_years_experience, normalize_date
from src.normalizers.location import normalize_country, parse_location_string
from src.normalizers.phone import normalize_phone, normalize_phones
from src.normalizers.skills import canonicalize_skill, canonicalize_skills


class TestPhoneNormalizer:
    """Tests for normalize_phone and normalize_phones."""

    def test_us_number_formats_to_e164(self):
        """(555) 123-4567 → +15551234567"""
        # TODO: assert normalize_phone("(555) 123-4567") == "+15551234567"
        pytest.skip("Not yet implemented")

    def test_international_with_country_code(self):
        """Indian mobile with country code → E.164"""
        # TODO: assert normalize_phone("+91 99999 99999") == "+919999999999"
        pytest.skip("Not yet implemented")

    def test_invalid_number_returns_none(self):
        """Clearly invalid input should return None, never raise."""
        # TODO: assert normalize_phone("not-a-phone") is None
        # TODO: assert normalize_phone("") is None
        pytest.skip("Not yet implemented")

    def test_normalize_phones_deduplicates(self):
        """Same number in different formats should appear once in output."""
        # TODO: result = normalize_phones(["(555) 123-4567", "5551234567"])
        # TODO: assert result == ["+15551234567"]
        pytest.skip("Not yet implemented")

    def test_normalize_phones_drops_invalid(self):
        """Invalid entries in the list should be silently dropped."""
        # TODO: result = normalize_phones(["(555) 123-4567", "garbage"])
        # TODO: assert "garbage" not in result
        pytest.skip("Not yet implemented")


class TestDateNormalizer:
    """Tests for normalize_date and compute_years_experience."""

    def test_month_name_year(self):
        """'March 2021' → '2021-03'"""
        # TODO: assert normalize_date("March 2021") == "2021-03"
        pytest.skip("Not yet implemented")

    def test_iso_format_truncated_to_month(self):
        """'2021-03-15' → '2021-03'"""
        pytest.skip("Not yet implemented")

    def test_present_returns_none(self):
        """'Present', 'Current', 'now' → None"""
        # TODO: for token in ["Present", "current", "NOW", "ongoing"]:
        # TODO:     assert normalize_date(token) is None
        pytest.skip("Not yet implemented")

    def test_year_only_defaults_january(self):
        """'2021' → '2021-01'"""
        pytest.skip("Not yet implemented")

    def test_garbage_returns_none(self):
        """Unparseable input → None, never raises."""
        # TODO: assert normalize_date("not-a-date") is None
        pytest.skip("Not yet implemented")

    def test_compute_years_non_overlapping(self):
        """Two back-to-back 1-year stints → 2.0 years."""
        pytest.skip("Not yet implemented")

    def test_compute_years_overlapping(self):
        """Overlapping periods should not double-count."""
        # The union of overlapping intervals should be computed correctly.
        pytest.skip("Not yet implemented")

    def test_compute_years_current_role(self):
        """A current role (end=None) counts up to today."""
        pytest.skip("Not yet implemented")

    def test_compute_years_no_valid_dates(self):
        """No valid date ranges → None, not 0."""
        pytest.skip("Not yet implemented")


class TestLocationNormalizer:
    """Tests for normalize_country and parse_location_string."""

    def test_full_country_name(self):
        """'United States' → 'US'"""
        # TODO: assert normalize_country("United States") == "US"
        pytest.skip("Not yet implemented")

    def test_alpha3_code(self):
        """'IND' → 'IN'"""
        pytest.skip("Not yet implemented")

    def test_already_alpha2_passthrough(self):
        """'IN' → 'IN'"""
        pytest.skip("Not yet implemented")

    def test_case_insensitive(self):
        """'india' → 'IN'"""
        pytest.skip("Not yet implemented")

    def test_unknown_country_returns_none(self):
        """Unrecognizable country → None, never raises."""
        # TODO: assert normalize_country("Narnia") is None
        pytest.skip("Not yet implemented")

    def test_parse_three_part_location(self):
        """'San Francisco, CA, US' → {city, region, country}"""
        pytest.skip("Not yet implemented")

    def test_parse_city_only(self):
        """'Bangalore' → {city: 'Bangalore', region: None, country: None}"""
        pytest.skip("Not yet implemented")


class TestSkillNormalizer:
    """Tests for canonicalize_skill and canonicalize_skills."""

    def test_known_alias_maps_to_canonical(self):
        """'JS' → 'JavaScript'"""
        # TODO: assert canonicalize_skill("JS") == "JavaScript"
        pytest.skip("Not yet implemented")

    def test_case_insensitive_lookup(self):
        """'PYTHON' and 'python' both → 'Python'"""
        pytest.skip("Not yet implemented")

    def test_unknown_skill_passthrough_title_cased(self):
        """Unknown skill should return title-cased raw value."""
        # TODO: assert canonicalize_skill("my_custom_lib") == "My_Custom_Lib"
        pytest.skip("Not yet implemented")

    def test_deduplicates_by_canonical_name(self):
        """'JS' and 'JavaScript' in input should yield one 'JavaScript' in output."""
        # TODO: result = canonicalize_skills(["JS", "JavaScript", "python"])
        # TODO: assert result.count("JavaScript") == 1
        pytest.skip("Not yet implemented")
