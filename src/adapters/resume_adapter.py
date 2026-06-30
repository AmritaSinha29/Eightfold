"""Adapter for resume files (.pdf and .docx)."""
from __future__ import annotations

import logging
import re
from pathlib import Path

from src.adapters.base import BaseAdapter
from src.models.raw_record import RawEducation, RawExperience, RawRecord, RawSkill

logger = logging.getLogger(__name__)

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_PHONE_RE = re.compile(
    r"(?:\+\d{1,3}[\s\-]?)?(?:\(\d{3}\)|\d{3})[\s\-]?\d{3}[\s\-]?\d{4}"
)


class ResumeAdapter(BaseAdapter):
    """Extracts candidate information from PDF and DOCX resume files."""

    SOURCE_NAME = "resume"

    SUPPORTED_EXTENSIONS = frozenset({".pdf", ".docx", ".doc"})

    SECTION_KEYWORDS: dict[str, list[str]] = {
        "experience": ["experience", "work experience", "employment", "work history"],
        "education":  ["education", "academic background", "qualifications"],
        "skills":     ["skills", "technical skills", "competencies", "technologies"],
    }

    def can_handle(self, path: str) -> bool:
        return Path(path).suffix.lower() in self.SUPPORTED_EXTENSIONS

    def load(self, path: str) -> list[RawRecord]:
        try:
            suffix = Path(path).suffix.lower()
            text = self._load_pdf(path) if suffix == ".pdf" else self._load_docx(path)
            if not text.strip():
                return []
            return [self._parse_text(text, path)]
        except Exception as exc:
            logger.warning("Resume extraction failed for %s: %s", path, exc)
            return []

    def _load_pdf(self, path: str) -> str:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)

    def _load_docx(self, path: str) -> str:
        import docx
        doc = docx.Document(path)
        return "\n".join(p.text for p in doc.paragraphs)

    def _parse_text(self, text: str, source_path: str) -> RawRecord:
        sections = self._split_sections(text)
        return RawRecord(
            source_name=self.SOURCE_NAME,
            source_path=source_path,
            emails=self._extract_emails(text),
            phones=self._extract_phones(text),
            skills=self._parse_skills_block(sections.get("skills", "")),
            experience=self._parse_experience_block(sections.get("experience", "")),
            education=self._parse_education_block(sections.get("education", "")),
        )

    def _extract_emails(self, text: str) -> list[str]:
        return list(dict.fromkeys(m.lower() for m in _EMAIL_RE.findall(text)))

    def _extract_phones(self, text: str) -> list[str]:
        return list(dict.fromkeys(_PHONE_RE.findall(text)))

    def _split_sections(self, text: str) -> dict[str, str]:
        sections: dict[str, str] = {}
        current: str | None = None
        buffer: list[str] = []

        for line in text.split("\n"):
            stripped = line.strip().lower()
            matched_section = next(
                (sec for sec, kws in self.SECTION_KEYWORDS.items()
                 if any(stripped == kw or stripped.startswith(kw) for kw in kws)),
                None,
            )
            if matched_section:
                if current and buffer:
                    sections[current] = "\n".join(buffer).strip()
                current = matched_section
                buffer = []
            elif current:
                buffer.append(line)

        if current and buffer:
            sections[current] = "\n".join(buffer).strip()
        return sections

    def _parse_experience_block(self, block: str) -> list[RawExperience]:
        if not block:
            return []
        entries = []
        for chunk in re.split(r"\n\s*\n", block):
            lines = [l.strip() for l in chunk.strip().split("\n") if l.strip()]
            if not lines:
                continue
            date_pattern = re.compile(
                r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|\d{4})",
                re.IGNORECASE,
            )
            dates = date_pattern.findall(chunk)
            entries.append(RawExperience(
                company=lines[0] if lines else None,
                title=lines[1] if len(lines) > 1 else None,
                start=dates[0] if dates else None,
                end=dates[1] if len(dates) > 1 else None,
            ))
        return entries

    def _parse_education_block(self, block: str) -> list[RawEducation]:
        if not block:
            return []
        entries = []
        for chunk in re.split(r"\n\s*\n", block):
            lines = [l.strip() for l in chunk.strip().split("\n") if l.strip()]
            if not lines:
                continue
            year_m = re.search(r"\b(19|20)\d{2}\b", chunk)
            entries.append(RawEducation(
                institution=lines[0],
                degree=lines[1] if len(lines) > 1 else None,
                end_year=year_m.group(0) if year_m else None,
            ))
        return entries

    def _parse_skills_block(self, block: str) -> list[RawSkill]:
        if not block:
            return []
        raw_items = re.split(r"[,\n•\-\|/]", block)
        return [
            RawSkill(name=s.strip(), source_name=self.SOURCE_NAME)
            for s in raw_items
            if s.strip()
        ]
