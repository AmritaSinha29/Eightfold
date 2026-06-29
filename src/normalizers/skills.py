"""Skill name canonicalization using a data-driven alias map.

The alias map (data/skill_aliases.json) maps lowercase raw names → canonical names,
e.g. {"js": "JavaScript", "reactjs": "React"}. The map is loaded once at pipeline
startup and cached at module level for performance.

Updating the skill taxonomy requires no code changes — only a JSON edit.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


# Module-level cache — populated by load_alias_map().
_ALIAS_MAP: dict[str, str] = {}
_ALIAS_MAP_LOADED: bool = False

# Default path relative to the project root.
_DEFAULT_MAP_PATH = Path(__file__).parent.parent.parent / "data" / "skill_aliases.json"


def load_alias_map(path: Optional[str] = None) -> None:
    """Load the skill alias map from disk into the module-level cache.

    Safe to call multiple times — subsequent calls are no-ops if the map
    is already loaded (unless a new path is explicitly provided).

    Args:
        path: Path to skill_aliases.json. Defaults to data/skill_aliases.json
              relative to the project root.
    """
    global _ALIAS_MAP, _ALIAS_MAP_LOADED
    # TODO: Resolve path: use provided path or _DEFAULT_MAP_PATH
    # TODO: open + json.load
    # TODO: Build lowercase lookup: {raw.lower().strip(): canonical for raw, canonical in data.items()}
    # TODO: _ALIAS_MAP = lowercase_map
    # TODO: _ALIAS_MAP_LOADED = True
    raise NotImplementedError


def canonicalize_skill(raw: str) -> str:
    """Map a raw skill name to its canonical form.

    If the raw name (lowercased, stripped) is in the alias map, return
    the canonical name. Otherwise return the raw name title-cased
    (pass-through with minimal normalization).

    Args:
        raw: Raw skill name, e.g. "JS", "react.js", "Machine Learning".

    Returns:
        Canonical skill name, e.g. "JavaScript", "React", "Machine Learning".

    Examples:
        >>> canonicalize_skill("JS")
        'JavaScript'
        >>> canonicalize_skill("unknown_tool_xyz")
        'Unknown_Tool_Xyz'
    """
    # TODO: If not _ALIAS_MAP_LOADED: call load_alias_map()
    # TODO: key = raw.strip().lower()
    # TODO: return _ALIAS_MAP.get(key, raw.strip().title())
    raise NotImplementedError


def canonicalize_skills(raws: list[str]) -> list[str]:
    """Canonicalize a list of skill names, deduplicating by canonical form.

    Deduplication is by canonical name (so "JS" and "JavaScript" in the
    same list collapse to one entry; first occurrence wins).

    Args:
        raws: List of raw skill name strings.

    Returns:
        Deduplicated list of canonical skill names.
    """
    # TODO: [canonicalize_skill(r) for r in raws]
    # TODO: Deduplicate preserving order: list(dict.fromkeys(...))
    raise NotImplementedError
