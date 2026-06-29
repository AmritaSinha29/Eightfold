"""Adapter for recruiter CSV exports.

Expected columns (case-insensitive): name, email, phone, current_company, title.
Extra columns are stored in RawRecord.extra.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional

from src.adapters.base import BaseAdapter
from src.models.raw_record import RawExperience, RawRecord


class CSVAdapter(BaseAdapter):
    """Reads recruiter CSV exports and emits one RawRecord per candidate row.

    The adapter resolves column headers case-insensitively and supports
    common aliases (e.g. "full_name" for "name"). Any column that does not
    map to a canonical field is stored in RawRecord.extra.
    """

    SOURCE_NAME = "csv"

    # Maps canonical internal field → acceptable CSV header aliases (lowercase).
    FIELD_ALIASES: dict[str, list[str]] = {
        "name": ["name", "full_name", "candidate_name", "candidate"],
        "email": ["email", "email_address", "e-mail", "emailaddress"],
        "phone": ["phone", "phone_number", "mobile", "cell", "telephone"],
        "current_company": ["current_company", "company", "employer", "organization"],
        "title": ["title", "job_title", "position", "role"],
    }

    def can_handle(self, path: str) -> bool:
        """Return True if the path has a .csv extension.

        Args:
            path: File path to check.
        """
        # TODO: return Path(path).suffix.lower() == ".csv"
        raise NotImplementedError

    def load(self, path: str) -> list[RawRecord]:
        """Parse a CSV file and return one RawRecord per non-empty row.

        Tries UTF-8 encoding first, falls back to latin-1.
        Returns [] on FileNotFoundError, csv.Error, or any other exception.

        Args:
            path: Path to the .csv file.

        Returns:
            List of RawRecord objects; empty list on any failure.
        """
        # TODO: Try open(path, encoding="utf-8"), fallback to "latin-1"
        # TODO: csv.DictReader over the file
        # TODO: _resolve_header(reader.fieldnames) → header_map
        # TODO: [_row_to_record(row, header_map) for row in reader if any(row.values())]
        # TODO: Catch FileNotFoundError, csv.Error, Exception → log warning, return []
        raise NotImplementedError

    def _resolve_header(self, fieldnames: list[str]) -> dict[str, Optional[str]]:
        """Build a mapping of canonical field → actual CSV header, or None if absent.

        Args:
            fieldnames: Header strings as reported by csv.DictReader.

        Returns:
            Dict like {"name": "full_name", "email": None, ...} where None means
            the column was not found in this file.
        """
        # TODO: Lowercase + strip each header
        # TODO: For each canonical field, find first matching alias in lowercased headers
        # TODO: Return dict {canonical: actual_header_or_None}
        raise NotImplementedError

    def _row_to_record(
        self,
        row: dict[str, str],
        header_map: dict[str, Optional[str]],
    ) -> RawRecord:
        """Convert one CSV row to a RawRecord.

        Args:
            row: Raw row dict from csv.DictReader.
            header_map: Output of _resolve_header.

        Returns:
            A RawRecord with fields populated from the row.
        """
        # TODO: Extract name → full_name (strip)
        # TODO: Extract email → emails list (non-empty only)
        # TODO: Extract phone → phones list (raw, pre-E.164)
        # TODO: Build RawExperience(company=current_company, title=title) → experience[0]
        # TODO: All unmapped columns → extra dict
        # TODO: Return RawRecord(source_name=self.SOURCE_NAME, source_path=..., ...)
        raise NotImplementedError
