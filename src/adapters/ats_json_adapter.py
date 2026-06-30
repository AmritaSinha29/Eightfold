"""Adapter for ATS JSON blobs with non-canonical field names."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional

from src.adapters.base import BaseAdapter
from src.models.raw_record import RawEducation, RawExperience, RawRecord, RawSkill

logger = logging.getLogger(__name__)


class ATSJsonAdapter(BaseAdapter):
    """Reads ATS JSON blobs and maps vendor-specific fields to RawRecord."""

    SOURCE_NAME = "ats_json"

    DEFAULT_FIELD_MAP: dict[str, str] = {
        "candidate_name":    "full_name",
        "primary_email":     "emails",
        "cell_phone":        "phones",
        "city":              "location_city",
        "state":             "location_region",
        "country":           "location_country",
        "linkedin_url":      "linkedin_url",
        "github_url":        "github_url",
        "portfolio_url":     "portfolio_url",
        "headline":          "headline",
        "years_experience":  "years_experience",
    }

    # Fields that require special handling beyond simple scalar assignment.
    _LIST_FIELDS = {"emails", "phones"}
    _SKILLS_KEY = "skills_raw"
    _EXPERIENCE_KEY = "experience"
    _EDUCATION_KEY = "education"

    def __init__(self, field_map: Optional[dict[str, str]] = None) -> None:
        self.field_map: dict[str, str] = {**self.DEFAULT_FIELD_MAP, **(field_map or {})}

    def can_handle(self, path: str) -> bool:
        p = Path(path)
        return p.suffix.lower() == ".json" and "linkedin" not in p.stem.lower()

    def load(self, path: str) -> list[RawRecord]:
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            logger.warning("ATS JSON file not found: %s", path)
            return []
        except json.JSONDecodeError as exc:
            logger.warning("ATS JSON decode error in %s: %s", path, exc)
            return []
        except Exception as exc:
            logger.warning("Unexpected error loading %s: %s", path, exc)
            return []

        if isinstance(data, list):
            entries = data
        elif isinstance(data, dict) and "candidates" in data:
            entries = data["candidates"]
        elif isinstance(data, dict):
            entries = [data]
        else:
            return []

        return [self._entry_to_record(entry, path) for entry in entries if isinstance(entry, dict)]

    def _entry_to_record(self, entry: dict[str, Any], source_path: str) -> RawRecord:
        record = RawRecord(source_name=self.SOURCE_NAME, source_path=source_path)
        mapped_keys: set[str] = set()

        for ats_key, canonical in self.field_map.items():
            value = self._get_nested(entry, ats_key)
            if value is None:
                continue
            mapped_keys.add(ats_key.split(".")[0])

            if canonical == "emails":
                vals = value if isinstance(value, list) else [value]
                record.emails.extend(str(v).strip() for v in vals if v)
            elif canonical == "phones":
                vals = value if isinstance(value, list) else [value]
                record.phones.extend(str(v).strip() for v in vals if v)
            elif canonical == "years_experience":
                try:
                    record.years_experience = float(value)
                except (ValueError, TypeError):
                    pass
            elif hasattr(record, canonical):
                setattr(record, canonical, str(value).strip() if value else None)

        # Skills array
        skills_raw = entry.get(self._SKILLS_KEY)
        if skills_raw and isinstance(skills_raw, list):
            mapped_keys.add(self._SKILLS_KEY)
            record.skills = [RawSkill(name=str(s).strip(), source_name=self.SOURCE_NAME) for s in skills_raw if s]

        # Experience array
        experience_raw = entry.get(self._EXPERIENCE_KEY)
        if experience_raw and isinstance(experience_raw, list):
            mapped_keys.add(self._EXPERIENCE_KEY)
            record.experience = [self._parse_experience(e) for e in experience_raw if isinstance(e, dict)]

        # Education array
        education_raw = entry.get(self._EDUCATION_KEY)
        if education_raw and isinstance(education_raw, list):
            mapped_keys.add(self._EDUCATION_KEY)
            record.education = [self._parse_education(e) for e in education_raw if isinstance(e, dict)]

        # Unmapped keys → extra
        record.extra = {k: v for k, v in entry.items() if k not in mapped_keys and k not in self.field_map}

        return record

    def _parse_experience(self, e: dict[str, Any]) -> RawExperience:
        return RawExperience(
            company=e.get("company") or e.get("companyName") or e.get("employer"),
            title=e.get("title") or e.get("position") or e.get("role"),
            start=e.get("start") or e.get("start_date") or e.get("startDate"),
            end=e.get("end") or e.get("end_date") or e.get("endDate"),
            summary=e.get("summary") or e.get("description"),
        )

    def _parse_education(self, e: dict[str, Any]) -> RawEducation:
        return RawEducation(
            institution=e.get("institution") or e.get("school") or e.get("schoolName"),
            degree=e.get("degree") or e.get("degreeName"),
            field=e.get("field") or e.get("fieldOfStudy"),
            end_year=str(e["end_year"]) if e.get("end_year") else None,
        )

    def _get_nested(self, data: dict[str, Any], dotted_key: str) -> Any:
        node: Any = data
        for segment in dotted_key.split("."):
            if not isinstance(node, dict):
                return None
            node = node.get(segment)
            if node is None:
                return None
        return node

    @staticmethod
    def load_field_map(map_path: str) -> dict[str, str]:
        with open(map_path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in data.items()):
            raise ValueError(f"ATS field map must be a flat {{str: str}} JSON object: {map_path}")
        return data
