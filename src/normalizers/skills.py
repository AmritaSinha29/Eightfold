"""Skill name canonicalization using a data-driven alias map.

The alias map (data/skill_aliases.json) maps lowercase raw names to canonical names.
Loaded once at pipeline startup and cached at module level.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


_ALIAS_MAP: dict[str, str] = {}
_ALIAS_MAP_LOADED: bool = False

_DEFAULT_MAP_PATH = Path(__file__).parent.parent.parent / "data" / "skill_aliases.json"


def load_alias_map(path: Optional[str] = None) -> None:
    """Load the skill alias map from disk into the module-level cache.

    Safe to call multiple times — a no-op if already loaded and no new path given.
    """
    global _ALIAS_MAP, _ALIAS_MAP_LOADED
    if _ALIAS_MAP_LOADED and path is None:
        return
    target = Path(path) if path else _DEFAULT_MAP_PATH
    with open(target, encoding="utf-8") as f:
        data = json.load(f)
    _ALIAS_MAP = {k.lower().strip(): v for k, v in data.items()}
    _ALIAS_MAP_LOADED = True


def canonicalize_skill(raw: str) -> str:
    """Map a raw skill name to its canonical form via the alias map.

    Falls back to title-cased raw name if no alias is found.
    """
    if not _ALIAS_MAP_LOADED:
        load_alias_map()
    return _ALIAS_MAP.get(raw.strip().lower(), raw.strip().title())


def canonicalize_skills(raws: list[str]) -> list[str]:
    """Canonicalize a list of skill names, deduplicating by canonical form."""
    return list(dict.fromkeys(canonicalize_skill(r) for r in raws))
