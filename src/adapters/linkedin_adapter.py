"""Adapter for LinkedIn data exports (pre-exported JSON file).

IMPORTANT: LinkedIn has no public API and scraping violates their ToS.
This adapter accepts a pre-exported or mocked JSON file only.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from src.adapters.base import BaseAdapter
from src.models.raw_record import RawEducation, RawExperience, RawRecord, RawSkill

logger = logging.getLogger(__name__)


class LinkedInAdapter(BaseAdapter):
    """Reads a LinkedIn data export JSON and returns a single RawRecord."""

    SOURCE_NAME = "linkedin"

    def can_handle(self, path: str) -> bool:
        p = Path(path)
        return p.suffix.lower() == ".json" and "linkedin" in p.stem.lower()

    def load(self, path: str) -> list[RawRecord]:
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            return [self._entry_to_record(data, path)]
        except FileNotFoundError:
            logger.warning("LinkedIn export not found: %s", path)
            return []
        except json.JSONDecodeError as exc:
            logger.warning("LinkedIn JSON decode error in %s: %s", path, exc)
            return []
        except Exception as exc:
            logger.warning("Unexpected error loading %s: %s", path, exc)
            return []

    def _entry_to_record(self, data: dict[str, Any], source_path: str) -> RawRecord:
        first = data.get("firstName", "").strip()
        last = data.get("lastName", "").strip()
        full_name = f"{first} {last}".strip() or None

        email = data.get("emailAddress")
        emails = [email] if email else []

        skills = [
            RawSkill(name=str(s).strip(), source_name=self.SOURCE_NAME)
            for s in data.get("skills", [])
            if s
        ]

        positions = [self._parse_position(p) for p in data.get("positions", [])]
        educations = [self._parse_education(e) for e in data.get("educations", [])]

        # geoLocationName is a freeform string; kept raw for the normalizer
        geo = data.get("geoLocationName")

        return RawRecord(
            source_name=self.SOURCE_NAME,
            source_path=source_path,
            full_name=full_name,
            emails=emails,
            headline=data.get("headline"),
            location_city=geo,
            skills=skills,
            experience=positions,
            education=educations,
        )

    def _parse_position(self, pos: dict[str, Any]) -> RawExperience:
        time_period = pos.get("timePeriod") or {}
        start_date = time_period.get("startDate") or {}
        end_date = time_period.get("endDate")

        start: str | None = None
        if start_date:
            m = start_date.get("month", 1)
            y = start_date.get("year")
            if y:
                start = f"{m}/{y}"

        end: str | None = None
        if end_date:
            m = end_date.get("month", 1)
            y = end_date.get("year")
            if y:
                end = f"{m}/{y}"

        return RawExperience(
            company=pos.get("companyName"),
            title=pos.get("title"),
            start=start,
            end=end,
            summary=pos.get("description"),
        )

    def _parse_education(self, edu: dict[str, Any]) -> RawEducation:
        time_period = edu.get("timePeriod") or {}
        end_date = time_period.get("endDate") or {}
        end_year = end_date.get("year") if end_date else None

        return RawEducation(
            institution=edu.get("schoolName"),
            degree=edu.get("degreeName"),
            field=edu.get("fieldOfStudy"),
            end_year=str(end_year) if end_year else None,
        )
