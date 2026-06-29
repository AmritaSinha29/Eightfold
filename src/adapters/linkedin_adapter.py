"""Adapter for LinkedIn data.

IMPORTANT: LinkedIn has no public API and scraping violates their Terms of Service.
This adapter accepts a pre-exported JSON file (LinkedIn data export, or a mock
produced for testing). This limitation is documented in the README.

In a production system this would integrate with a licensed data provider
(e.g., Proxycurl, People Data Labs).

Expected JSON shape (LinkedIn data export or compatible mock):
{
  "firstName": "Alice",
  "lastName": "Johnson",
  "headline": "Software Engineer | Python",
  "geoLocationName": "San Francisco Bay Area",
  "positions": [
    {
      "companyName": "Acme Corp",
      "title": "Software Engineer",
      "timePeriod": {"startDate": {"month": 3, "year": 2022}, "endDate": null},
      "description": "..."
    }
  ],
  "educations": [
    {
      "schoolName": "UC Berkeley",
      "degreeName": "Bachelor of Science",
      "fieldOfStudy": "Computer Science",
      "timePeriod": {"endDate": {"year": 2022}}
    }
  ]
}
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.adapters.base import BaseAdapter
from src.models.raw_record import RawEducation, RawExperience, RawRecord


class LinkedInAdapter(BaseAdapter):
    """Reads LinkedIn data from a pre-exported or mocked JSON file."""

    SOURCE_NAME = "linkedin"

    def can_handle(self, path: str) -> bool:
        """Return True if path ends with .json and contains 'linkedin' in the filename.

        Args:
            path: File path to check.
        """
        # TODO: p = Path(path); p.suffix.lower() == ".json" and "linkedin" in p.stem.lower()
        raise NotImplementedError

    def load(self, path: str) -> list[RawRecord]:
        """Parse a LinkedIn export JSON and return a single-element RawRecord list.

        Args:
            path: Path to the LinkedIn JSON export file.

        Returns:
            [RawRecord] on success; [] on FileNotFoundError, JSONDecodeError, or
            any other failure.
        """
        # TODO: open + json.load
        # TODO: return [_entry_to_record(data)]
        # TODO: Catch FileNotFoundError, json.JSONDecodeError → return []
        raise NotImplementedError

    def _entry_to_record(self, data: dict[str, Any]) -> RawRecord:
        """Map LinkedIn JSON fields to a RawRecord.

        Args:
            data: Parsed JSON dict from the LinkedIn export file.

        Returns:
            Populated RawRecord.
        """
        # TODO: full_name = (data.get("firstName", "") + " " + data.get("lastName", "")).strip()
        # TODO: headline = data.get("headline")
        # TODO: location from geoLocationName (raw, pre-normalization)
        # TODO: positions → [_parse_position(p) for p in data.get("positions", [])]
        # TODO: educations → [_parse_education(e) for e in data.get("educations", [])]
        # TODO: Return RawRecord(source_name=self.SOURCE_NAME, source_path=..., ...)
        raise NotImplementedError

    def _parse_position(self, pos: dict[str, Any]) -> RawExperience:
        """Convert one LinkedIn position entry to RawExperience.

        Args:
            pos: One element from the "positions" array.

        Returns:
            RawExperience with raw date strings.
        """
        # TODO: company = pos.get("companyName")
        # TODO: title = pos.get("title")
        # TODO: Extract startDate: {"month": M, "year": Y} → raw string "M/Y"
        # TODO: Extract endDate: null → None (current role), else "M/Y"
        # TODO: description → summary
        raise NotImplementedError

    def _parse_education(self, edu: dict[str, Any]) -> RawEducation:
        """Convert one LinkedIn education entry to RawEducation.

        Args:
            edu: One element from the "educations" array.

        Returns:
            RawEducation with raw field values.
        """
        # TODO: institution = edu.get("schoolName")
        # TODO: degree = edu.get("degreeName")
        # TODO: field = edu.get("fieldOfStudy")
        # TODO: end_year = str(edu.get("timePeriod", {}).get("endDate", {}).get("year"))
        raise NotImplementedError
