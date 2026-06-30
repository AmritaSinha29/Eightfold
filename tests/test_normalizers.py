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
        """(415) 555-0101 → +14155550101"""
        assert normalize_phone("(415) 555-0101") == "+14155550101"

    def test_international_with_country_code(self):
        """Indian mobile with country code → E.164"""
        assert normalize_phone("+91 99999 99999") == "+919999999999"

    def test_invalid_number_returns_none(self):
        """Clearly invalid input should return None, never raise."""
        assert normalize_phone("not-a-phone") is None
        assert normalize_phone("") is None

    def test_normalize_phones_deduplicates(self):
        """Same number in different formats should appear once in output."""
        result = normalize_phones(["(415) 555-0101", "4155550101"])
        assert result == ["+14155550101"]

    def test_normalize_phones_drops_invalid(self):
        """Invalid entries in the list should be silently dropped."""
        result = normalize_phones(["(415) 555-0101", "garbage"])
        assert len(result) == 1
        assert "garbage" not in result


class TestDateNormalizer:
    """Tests for normalize_date and compute_years_experience."""

    def test_month_name_year(self):
        """'March 2021' → '2021-03'"""
        assert normalize_date("March 2021") == "2021-03"

    def test_iso_format_truncated_to_month(self):
        """'2021-03-15' → '2021-03'"""
        assert normalize_date("2021-03-15") == "2021-03"

    def test_present_returns_none(self):
        """'Present', 'Current', 'now' → None"""
        for token in ["Present", "current", "NOW", "ongoing"]:
            assert normalize_date(token) is None

    def test_year_only_produces_yyyy_mm(self):
        """'2021' → 'YYYY-MM' string with year 2021 (month defaults to current month)."""
        result = normalize_date("2021")
        assert result is not None
        assert result.startswith("2021-")

    def test_garbage_returns_none(self):
        """Unparseable input → None, never raises."""
        assert normalize_date("not-a-date") is None

    def test_compute_years_non_overlapping(self):
        """Two back-to-back 1-year stints → 2.0 years."""
        exps = [
            {"start": "2019-01", "end": "2020-01"},
            {"start": "2020-01", "end": "2021-01"},
        ]
        result = compute_years_experience(exps)
        assert result == 2.0

    def test_compute_years_overlapping(self):
        """Overlapping periods should not double-count."""
        exps = [
            {"start": "2019-01", "end": "2021-01"},
            {"start": "2020-01", "end": "2022-01"},
        ]
        result = compute_years_experience(exps)
        assert result == 3.0

    def test_compute_years_current_role(self):
        """A current role (end=None) counts up to today."""
        exps = [{"start": "2020-01", "end": None}]
        result = compute_years_experience(exps)
        assert result is not None
        assert result > 0

    def test_compute_years_no_valid_dates(self):
        """No valid date ranges → None, not 0."""
        result = compute_years_experience([{"start": None, "end": None}])
        assert result is None


class TestLocationNormalizer:
    """Tests for normalize_country and parse_location_string."""

    def test_full_country_name(self):
        """'United States' → 'US'"""
        assert normalize_country("United States") == "US"

    def test_alpha3_code(self):
        """'IND' → 'IN'"""
        assert normalize_country("IND") == "IN"

    def test_already_alpha2_passthrough(self):
        """'IN' → 'IN'"""
        assert normalize_country("IN") == "IN"

    def test_case_insensitive(self):
        """'india' → 'IN'"""
        assert normalize_country("india") == "IN"

    def test_unknown_country_returns_none(self):
        """Unrecognizable country → None, never raises."""
        assert normalize_country("Zzzmadeupland") is None

    def test_parse_three_part_location(self):
        """'San Francisco, CA, US' → {city, region, country}"""
        result = parse_location_string("San Francisco, CA, US")
        assert result["city"] == "San Francisco"
        assert result["region"] == "CA"
        assert result["country"] == "US"

    def test_parse_city_only(self):
        """'Bangalore' → {city: 'Bangalore', region: None, country: None}"""
        result = parse_location_string("Bangalore")
        assert result["city"] == "Bangalore"
        assert result["region"] is None
        assert result["country"] is None


class TestSkillNormalizer:
    """Tests for canonicalize_skill and canonicalize_skills."""

    def test_known_alias_maps_to_canonical(self):
        """'JS' → 'JavaScript'"""
        assert canonicalize_skill("JS") == "JavaScript"

    def test_case_insensitive_lookup(self):
        """'PYTHON' and 'python' both → 'Python'"""
        assert canonicalize_skill("PYTHON") == "Python"
        assert canonicalize_skill("python") == "Python"

    def test_unknown_skill_passthrough_title_cased(self):
        """Unknown skill should return title-cased raw value."""
        assert canonicalize_skill("my_custom_lib") == "My_Custom_Lib"

    def test_deduplicates_by_canonical_name(self):
        """'JS' and 'JavaScript' in input should yield one 'JavaScript' in output."""
        result = canonicalize_skills(["JS", "JavaScript", "python"])
        assert result.count("JavaScript") == 1
