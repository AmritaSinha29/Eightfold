"""Adapter for recruiter free-text notes (.txt files)."""
from __future__ import annotations

import logging
import re
from pathlib import Path

from src.adapters.base import BaseAdapter
from src.models.raw_record import RawRecord, RawSkill

logger = logging.getLogger(__name__)

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_PHONE_RE = re.compile(
    r"(?:\+\d{1,3}[\s\-]?)?(?:\(\d{3}\)|\d{3})[\s\-]?\d{3}[\s\-]?\d{4}"
)


class NotesAdapter(BaseAdapter):
    """Extracts candidate signals from recruiter free-text .txt notes."""

    SOURCE_NAME = "notes"

    def can_handle(self, path: str) -> bool:
        return Path(path).suffix.lower() == ".txt"

    def load(self, path: str) -> list[RawRecord]:
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
            if not text.strip():
                return []
            return [self._parse_text(text, path)]
        except FileNotFoundError:
            logger.warning("Notes file not found: %s", path)
            return []
        except UnicodeDecodeError:
            logger.warning("Notes file encoding error: %s", path)
            return []

    def _parse_text(self, text: str, source_path: str) -> RawRecord:
        return RawRecord(
            source_name=self.SOURCE_NAME,
            source_path=source_path,
            full_name=self._extract_name(text),
            emails=self._extract_emails(text),
            phones=self._extract_phones(text),
            skills=self._extract_skills(text),
            extra={"confidence_hint": "low"},
        )

    def _extract_name(self, text: str) -> str | None:
        m = re.search(r"(?:name|candidate)\s*:\s*(.+)", text, re.IGNORECASE)
        return m.group(1).strip() if m else None

    def _extract_emails(self, text: str) -> list[str]:
        return list(dict.fromkeys(_EMAIL_RE.findall(text)))

    def _extract_phones(self, text: str) -> list[str]:
        return list(dict.fromkeys(_PHONE_RE.findall(text)))

    def _extract_skills(self, text: str) -> list[RawSkill]:
        from src.normalizers.skills import _ALIAS_MAP, _ALIAS_MAP_LOADED, load_alias_map
        if not _ALIAS_MAP_LOADED:
            load_alias_map()
        text_lower = text.lower()
        seen: set[str] = set()
        skills: list[RawSkill] = []
        # Match longest aliases first to avoid partial shadowing (e.g. "node" before "node.js")
        for alias in sorted(_ALIAS_MAP.keys(), key=len, reverse=True):
            if alias in text_lower and alias not in seen:
                seen.add(alias)
                canonical = _ALIAS_MAP[alias]
                # Avoid duplicate canonical names
                if canonical not in seen:
                    seen.add(canonical)
                    skills.append(RawSkill(name=alias, source_name=self.SOURCE_NAME))
        return skills
