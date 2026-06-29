"""Runtime output config parser and validator.

The config JSON controls:
- Which canonical fields are included in the output
- Renaming / remapping via "from" path expressions
- Per-field normalization (e.g. E164 for phones)
- Whether provenance and confidence are included
- How to handle missing values: null | omit | error
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Optional


@dataclass
class FieldSpec:
    """Specification for one output field declared in the config."""

    path: str                           # output key name, e.g. "primary_email"
    from_path: Optional[str] = None     # canonical path to read, e.g. "emails[0]"
    type: Optional[str] = None          # expected type hint: "string", "string[]", "number", "object"
    required: bool = False              # if True and value is missing, honor on_missing
    normalize: Optional[str] = None     # normalization to apply: "E164", "canonical", etc.


@dataclass
class OutputConfig:
    """Parsed and validated runtime output configuration."""

    fields: list[FieldSpec] = field(default_factory=list)
    include_confidence: bool = False
    include_provenance: bool = False
    on_missing: Literal["null", "omit", "error"] = "null"


def load_config(path: str) -> OutputConfig:
    """Load and parse a runtime output config JSON file.

    Args:
        path: Path to the config .json file.

    Returns:
        Validated OutputConfig object.

    Raises:
        FileNotFoundError: If path does not exist.
        ValueError: If the config JSON is malformed or fails schema validation.
    """
    # TODO: open + json.load
    # TODO: return parse_config(raw_dict)
    raise NotImplementedError


def parse_config(raw: dict[str, Any]) -> OutputConfig:
    """Parse a raw config dict (from JSON) into an OutputConfig.

    Args:
        raw: Dict parsed from the runtime config JSON.

    Returns:
        OutputConfig with all FieldSpec entries populated.

    Raises:
        ValueError: If required top-level keys are missing, on_missing is
                    invalid, or a field spec is malformed.
    """
    # TODO: Validate "fields" key exists and is a list
    # TODO: parse each field dict → FieldSpec(path=..., from_path=..., ...)
    # TODO: Validate on_missing in {"null", "omit", "error"}
    # TODO: Assemble and return OutputConfig
    raise NotImplementedError


def default_config() -> OutputConfig:
    """Return the default OutputConfig that emits all canonical schema fields.

    Used when no --config flag is provided on the CLI. Includes all fields,
    provenance, and confidence.

    Returns:
        OutputConfig with one FieldSpec per canonical field.
    """
    # TODO: Build one FieldSpec for each canonical field (candidate_id, full_name, ...)
    # TODO: include_confidence=True, include_provenance=True, on_missing="null"
    raise NotImplementedError
