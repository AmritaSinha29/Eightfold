"""Runtime output config parser."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Literal, Optional


@dataclass
class FieldSpec:
    path:       str
    from_path:  Optional[str] = None
    type:       Optional[str] = None
    required:   bool          = False
    normalize:  Optional[str] = None


@dataclass
class OutputConfig:
    fields:              list[FieldSpec] = field(default_factory=list)
    include_confidence:  bool            = False
    include_provenance:  bool            = False
    on_missing:          Literal["null", "omit", "error"] = "null"


def load_config(path: str) -> OutputConfig:
    """Load and parse a runtime output config JSON file."""
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return parse_config(raw)


def parse_config(raw: dict[str, Any]) -> OutputConfig:
    """Parse a raw config dict into an OutputConfig."""
    if "fields" not in raw or not isinstance(raw["fields"], list):
        raise ValueError("Config must contain a 'fields' list")

    on_missing = raw.get("on_missing", "null")
    if on_missing not in ("null", "omit", "error"):
        raise ValueError(f"on_missing must be 'null', 'omit', or 'error'; got {on_missing!r}")

    fields: list[FieldSpec] = []
    for item in raw["fields"]:
        if not isinstance(item, dict) or "path" not in item:
            raise ValueError(f"Each field spec must be a dict with 'path': {item!r}")
        fields.append(FieldSpec(
            path=item["path"],
            from_path=item.get("from"),
            type=item.get("type"),
            required=item.get("required", False),
            normalize=item.get("normalize"),
        ))

    return OutputConfig(
        fields=fields,
        include_confidence=raw.get("include_confidence", False),
        include_provenance=raw.get("include_provenance", False),
        on_missing=on_missing,
    )


def default_config() -> OutputConfig:
    """Return the default OutputConfig that emits all canonical schema fields."""
    fields = [
        FieldSpec(path="candidate_id",       type="string",   required=True),
        FieldSpec(path="full_name",           type="string"),
        FieldSpec(path="emails",              type="string[]"),
        FieldSpec(path="phones",              type="string[]"),
        FieldSpec(path="location",            type="object"),
        FieldSpec(path="links",               type="object"),
        FieldSpec(path="headline",            type="string"),
        FieldSpec(path="years_experience",    type="number"),
        FieldSpec(path="skills",              type="object[]"),
        FieldSpec(path="experience",          type="object[]"),
        FieldSpec(path="education",           type="object[]"),
    ]
    return OutputConfig(
        fields=fields,
        include_confidence=True,
        include_provenance=True,
        on_missing="null",
    )
