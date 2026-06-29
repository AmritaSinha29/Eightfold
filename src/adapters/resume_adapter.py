"""Adapter for resume files (.pdf and .docx).

Text extraction strategy:
- PDF: pdfplumber (layout-aware, better than pypdf for prose)
- DOCX: python-docx

Field extraction strategy:
- Regex for emails and phone numbers
- spacy NER for PERSON (name), ORG (company), DATE, GPE (location) if available
- Section-header detection for EXPERIENCE / EDUCATION / SKILLS blocks

All extracted fields are tagged with method="nlp_extract" in provenance,
signalling lower base confidence compared to structured sources.
"""
from __future__ import annotations

from pathlib import Path

from src.adapters.base import BaseAdapter
from src.models.raw_record import RawEducation, RawExperience, RawRecord, RawSkill


class ResumeAdapter(BaseAdapter):
    """Extracts candidate information from PDF and DOCX resume files.

    Confidence note: resume extraction is heuristic. The pipeline assigns
    lower base confidence to values from this source than to structured CSV/JSON.
    """

    SOURCE_NAME = "resume"

    SUPPORTED_EXTENSIONS = frozenset({".pdf", ".docx", ".doc"})

    # Common section headings used to split resume text into blocks.
    SECTION_KEYWORDS: dict[str, list[str]] = {
        "experience": ["experience", "work experience", "employment", "work history"],
        "education": ["education", "academic background", "qualifications"],
        "skills": ["skills", "technical skills", "competencies", "technologies"],
    }

    def can_handle(self, path: str) -> bool:
        """Return True if the file extension is .pdf, .docx, or .doc.

        Args:
            path: File path to check.
        """
        # TODO: Path(path).suffix.lower() in self.SUPPORTED_EXTENSIONS
        raise NotImplementedError

    def load(self, path: str) -> list[RawRecord]:
        """Extract a RawRecord from a resume file.

        Args:
            path: Absolute path to the .pdf or .docx file.

        Returns:
            [RawRecord] on success; [] on any extraction error.
        """
        # TODO: Route to _load_pdf or _load_docx based on suffix
        # TODO: raw_text = _load_pdf(path) or _load_docx(path)
        # TODO: return [_parse_text(raw_text, path)]
        # TODO: Catch all exceptions → return []
        raise NotImplementedError

    def _load_pdf(self, path: str) -> str:
        """Extract raw text from a PDF using pdfplumber.

        Args:
            path: Path to the PDF file.

        Returns:
            Concatenated text from all pages, pages separated by newlines.
        """
        # TODO: import pdfplumber
        # TODO: with pdfplumber.open(path) as pdf:
        # TODO:     return "\n".join(page.extract_text() or "" for page in pdf.pages)
        raise NotImplementedError

    def _load_docx(self, path: str) -> str:
        """Extract raw text from a DOCX file using python-docx.

        Args:
            path: Path to the DOCX file.

        Returns:
            Concatenated paragraph text.
        """
        # TODO: import docx
        # TODO: doc = docx.Document(path)
        # TODO: return "\n".join(p.text for p in doc.paragraphs)
        raise NotImplementedError

    def _parse_text(self, text: str, source_path: str) -> RawRecord:
        """Extract structured fields from raw resume text.

        Args:
            text: Full extracted text of the resume.
            source_path: Original file path (for RawRecord.source_path).

        Returns:
            Populated RawRecord.
        """
        # TODO: _extract_emails(text) → emails list
        # TODO: _extract_phones(text) → phones list
        # TODO: _extract_name(text) → full_name (spacy PERSON entity or first line)
        # TODO: _extract_location(text) → raw location string
        # TODO: _split_sections(text) → {section: block_text}
        # TODO: _parse_experience_block(blocks["experience"]) → experience list
        # TODO: _parse_education_block(blocks["education"]) → education list
        # TODO: _parse_skills_block(blocks["skills"]) → skills list
        # TODO: Return RawRecord(source_name=self.SOURCE_NAME, ...)
        raise NotImplementedError

    def _extract_emails(self, text: str) -> list[str]:
        """Find all email addresses in text using a regex pattern.

        Args:
            text: Raw text to search.

        Returns:
            List of unique email strings found.
        """
        # TODO: re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
        # TODO: Deduplicate, lowercase
        raise NotImplementedError

    def _extract_phones(self, text: str) -> list[str]:
        """Find all phone numbers in text using a flexible regex.

        Args:
            text: Raw text to search.

        Returns:
            List of raw phone strings found (pre-E.164 normalization).
        """
        # TODO: Pattern covering +1 (555) 123-4567, 555-123-4567, +91-9999999999
        # TODO: Return unique matches
        raise NotImplementedError

    def _split_sections(self, text: str) -> dict[str, str]:
        """Split resume text into named sections by detecting section headings.

        Args:
            text: Full resume text.

        Returns:
            Dict mapping section name → block text.
        """
        # TODO: Scan lines for headings matching SECTION_KEYWORDS (case-insensitive)
        # TODO: Accumulate text until the next heading
        # TODO: Return {section_name: accumulated_text}
        raise NotImplementedError

    def _parse_experience_block(self, block: str) -> list[RawExperience]:
        """Parse the EXPERIENCE section text into RawExperience entries.

        Args:
            block: Raw text of the experience section.
        """
        # TODO: Split block into individual job entries (blank-line or date-pattern heuristic)
        # TODO: Extract company, title, dates, description per entry
        raise NotImplementedError

    def _parse_education_block(self, block: str) -> list[RawEducation]:
        """Parse the EDUCATION section text into RawEducation entries.

        Args:
            block: Raw text of the education section.
        """
        # TODO: Extract institution, degree, field, graduation year
        raise NotImplementedError

    def _parse_skills_block(self, block: str) -> list[RawSkill]:
        """Parse the SKILLS section text into RawSkill entries.

        Args:
            block: Raw text of the skills section.
        """
        # TODO: Split by commas, bullets, newlines
        # TODO: Return [RawSkill(name=s.strip(), source_name="resume") for s in items]
        raise NotImplementedError
