"""Adapter for ATS JSON blobs with non-canonical field names.

Because every ATS vendor uses different field names, this adapter uses a
configurable field map to translate ATS keys into canonical RawRecord fields.
The map can be loaded from an external JSON file via load_field_map().
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from src.adapters.base import BaseAdapter
from src.models.raw_record import RawEducation, RawExperience, RawRecord, RawSkill


class ATSJsonAdapter(BaseAdapter):
    """Reads ATS JSON blobs and maps vendor-specific fields to RawRecord.

    The JSON may be a single candidate object or an array of objects.
    Nested ATS field paths (e.g. "contact.email") are supported in the
    field map using dot notation.
    """

    SOURCE_NAME = "ats_json"

    # Fallback mapping when no external map is provided.
    # Format: { ats_field_name_or_path: canonical_raw_record_attribute }
    DEFAULT_FIELD_MAP: dict[str, str] = {
        # TODO: Populate with real ATS examples after seeing sample data
        "candidate_name": "full_name",
        "primary_email": "emails",
        "cell_phone": "phones",
        "current_employer": "extra.current_company",
        "current_position": "extra.title",
        "city": "location_city",
        "state": "location_region",
        "country": "location_country",
    }

    def __init__(self, field_map: Optional[dict[str, str]] = None) -> None:
        """Initialize with an optional custom ATS field mapping.

        Args:
            field_map: Maps ATS field names → RawRecord attribute names.
                       If None, DEFAULT_FIELD_MAP is used.
        """
        # TODO: Merge provided field_map with DEFAULT_FIELD_MAP
        #       (provided values take precedence over defaults)
        self.field_map: dict[str, str] = field_map or dict(self.DEFAULT_FIELD_MAP)

    def can_handle(self, path: str) -> bool:
        """Return True if path has a .json extension.

        Args:
            path: File path to check.
        """
        # TODO: return Path(path).suffix.lower() == ".json"
        # TODO: Exclude linkedin_*.json which is handled by LinkedInAdapter
        raise NotImplementedError

    def load(self, path: str) -> list[RawRecord]:
        """Parse an ATS JSON file and return one RawRecord per candidate entry.

        The JSON root may be a dict (single candidate), a list of dicts, or
        an object with a "candidates" key containing a list.

        Args:
            path: Path to the .json file.

        Returns:
            List of RawRecord objects; empty list on any failure.
        """
        # TODO: open + json.load
        # TODO: Detect root shape: dict → [dict]; list → list; {"candidates": [...]} → list
        # TODO: [_entry_to_record(entry) for entry in entries]
        # TODO: Catch FileNotFoundError, json.JSONDecodeError, Exception → return []
        raise NotImplementedError

    def _entry_to_record(self, entry: dict[str, Any]) -> RawRecord:
        """Convert one ATS JSON entry dict to a RawRecord using self.field_map.

        Args:
            entry: Raw dict from the ATS JSON blob.

        Returns:
            Populated RawRecord; unmapped keys go to extra.
        """
        # TODO: Walk self.field_map: get_nested(entry, ats_key) → set on record
        # TODO: Handle list-typed fields (emails, phones, skills_raw)
        # TODO: Build RawExperience from experience sub-array if present
        # TODO: Store unmapped keys in extra
        raise NotImplementedError

    def _get_nested(self, data: dict[str, Any], dotted_key: str) -> Any:
        """Retrieve a value from a nested dict using dot-notation path.

        Args:
            data: The dict to traverse.
            dotted_key: Dot-separated key path, e.g. "contact.email".

        Returns:
            The value at the path, or None if any key is missing.
        """
        # TODO: Split dotted_key by "."
        # TODO: Walk data[k] for each segment, returning None on KeyError
        raise NotImplementedError

    @staticmethod
    def load_field_map(map_path: str) -> dict[str, str]:
        """Load an ATS field-map JSON file from disk.

        Args:
            map_path: Path to the ats_field_map.json file.

        Returns:
            Dict mapping ATS field names to RawRecord attribute names.

        Raises:
            FileNotFoundError: If map_path does not exist.
            ValueError: If the file is not a flat string→string JSON object.
        """
        # TODO: open + json.load
        # TODO: Validate it is a flat {str: str} dict
        # TODO: Raise ValueError with a clear message if not
        raise NotImplementedError
