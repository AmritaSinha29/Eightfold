"""Adapter for recruiter CSV exports."""
from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Optional

from src.adapters.base import BaseAdapter
from src.models.raw_record import RawExperience, RawRecord

logger = logging.getLogger(__name__)


class CSVAdapter(BaseAdapter):
    """Reads recruiter CSV exports and emits one RawRecord per candidate row."""

    SOURCE_NAME = "csv"

    FIELD_ALIASES: dict[str, list[str]] = {
        "name":            ["name", "full_name", "candidate_name", "candidate"],
        "email":           ["email", "email_address", "e-mail", "emailaddress"],
        "phone":           ["phone", "phone_number", "mobile", "cell", "telephone"],
        "current_company": ["current_company", "company", "employer", "organization"],
        "title":           ["title", "job_title", "position", "role"],
    }

    def can_handle(self, path: str) -> bool:
        return Path(path).suffix.lower() == ".csv"

    def load(self, path: str) -> list[RawRecord]:
        try:
            encoding = "utf-8"
            try:
                with open(path, encoding="utf-8") as probe:
                    probe.read()
            except UnicodeDecodeError:
                encoding = "latin-1"

            with open(path, encoding=encoding, newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                fieldnames = list(reader.fieldnames or [])

            header_map = self._resolve_header(fieldnames)
            return [
                self._row_to_record(row, header_map, path)
                for row in rows
                if any(v and v.strip() for v in row.values())
            ]
        except FileNotFoundError:
            logger.warning("CSV file not found: %s", path)
            return []
        except csv.Error as exc:
            logger.warning("CSV parse error in %s: %s", path, exc)
            return []
        except Exception as exc:
            logger.warning("Unexpected error loading %s: %s", path, exc)
            return []

    def _resolve_header(self, fieldnames: list[str]) -> dict[str, Optional[str]]:
        lowered = {h.lower().strip(): h for h in fieldnames}
        result: dict[str, Optional[str]] = {}
        for canonical, aliases in self.FIELD_ALIASES.items():
            result[canonical] = next(
                (lowered[alias] for alias in aliases if alias in lowered), None
            )
        return result

    def _row_to_record(
        self,
        row: dict[str, str],
        header_map: dict[str, Optional[str]],
        source_path: str,
    ) -> RawRecord:
        def get(field: str) -> Optional[str]:
            col = header_map.get(field)
            if col is None:
                return None
            val = row.get(col, "").strip()
            return val if val else None

        name = get("name")
        email = get("email")
        phone = get("phone")
        company = get("current_company")
        title = get("title")

        mapped_cols = {h for h in header_map.values() if h is not None}
        extra = {k: v for k, v in row.items() if k not in mapped_cols and v and v.strip()}

        experience = (
            [RawExperience(company=company, title=title)]
            if company or title
            else []
        )

        return RawRecord(
            source_name=self.SOURCE_NAME,
            source_path=source_path,
            full_name=name,
            emails=[email] if email else [],
            phones=[phone] if phone else [],
            experience=experience,
            extra=extra,
        )
