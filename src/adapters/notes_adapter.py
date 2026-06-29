"""Adapter for recruiter free-text notes (.txt files).

Notes are the least structured source. Extraction is purely regex +
heuristics. All extracted values are tagged with method="text_heuristic"
in provenance and receive low base confidence (0.40).
"""
from __future__ import annotations

from pathlib import Path

from src.adapters.base import BaseAdapter
from src.models.raw_record import RawRecord, RawSkill


class NotesAdapter(BaseAdapter):
    """Extracts candidate signals from recruiter free-text .txt notes.

    Looks for:
    - "Name:" / "Candidate:" prefixed lines → full_name
    - Email addresses via regex
    - Phone numbers via regex
    - Skill keywords from the skill_aliases map
    """

    SOURCE_NAME = "notes"

    def can_handle(self, path: str) -> bool:
        """Return True if path ends with .txt.

        Args:
            path: File path to check.
        """
        # TODO: Path(path).suffix.lower() == ".txt"
        raise NotImplementedError

    def load(self, path: str) -> list[RawRecord]:
        """Read a .txt file and extract a RawRecord via heuristics.

        Args:
            path: Path to the recruiter notes file.

        Returns:
            [RawRecord] on success; [] on FileNotFoundError or empty file.
        """
        # TODO: open(path, encoding="utf-8").read() → text
        # TODO: If text is blank/whitespace-only → return []
        # TODO: return [_parse_text(text, path)]
        # TODO: Catch FileNotFoundError, UnicodeDecodeError → return []
        raise NotImplementedError

    def _parse_text(self, text: str, source_path: str) -> RawRecord:
        """Apply heuristics to extract fields from unstructured note text.

        Args:
            text: Full content of the notes file.
            source_path: Original file path (for RawRecord.source_path).

        Returns:
            Populated RawRecord (many fields will be None; that is expected).
        """
        # TODO: _extract_name(text) → full_name (look for "Candidate:", "Name:" prefix)
        # TODO: _extract_emails(text) → emails list
        # TODO: _extract_phones(text) → phones list
        # TODO: _extract_skills(text) → skills list (keyword match against alias map keys)
        # TODO: Mark extra["confidence_hint"] = "low" to guide scorer
        # TODO: Return RawRecord(source_name=self.SOURCE_NAME, source_path=source_path, ...)
        raise NotImplementedError

    def _extract_name(self, text: str) -> str | None:
        """Look for "Name:" or "Candidate:" label on a line to extract a name.

        Args:
            text: Full notes text.

        Returns:
            Extracted name string, or None.
        """
        # TODO: re.search(r"(?:name|candidate)\s*:\s*(.+)", text, re.IGNORECASE)
        # TODO: Return match.group(1).strip() or None
        raise NotImplementedError

    def _extract_emails(self, text: str) -> list[str]:
        """Find email addresses in note text.

        Args:
            text: Full notes text.
        """
        # TODO: re.findall(email pattern, text)
        raise NotImplementedError

    def _extract_phones(self, text: str) -> list[str]:
        """Find phone numbers in note text.

        Args:
            text: Full notes text.
        """
        # TODO: re.findall(phone pattern, text)
        raise NotImplementedError

    def _extract_skills(self, text: str) -> list[RawSkill]:
        """Find skill mentions by matching against the skill alias map keys.

        Args:
            text: Full notes text.

        Returns:
            List of RawSkill objects for each alias found in the text.
        """
        # TODO: Load alias map keys (lowercase)
        # TODO: For each alias: if alias in text.lower() → append RawSkill
        # TODO: Deduplicate by name
        raise NotImplementedError
