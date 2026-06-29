"""Canonical profile — the clean internal record produced by the merger.

This is the single source of truth for one candidate after all sources have
been merged, normalized, and scored. It is NEVER serialized directly —
the projection layer reshapes it into the requested output format.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional


@dataclass
class CanonicalLocation:
    """Normalized location with ISO-3166 alpha-2 country code."""

    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None  # ISO-3166 alpha-2, e.g. "US", "IN"


@dataclass
class CanonicalLinks:
    """Collected profile URLs."""

    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    other: list[str] = field(default_factory=list)


@dataclass
class CanonicalSkill:
    """A skill with its canonical name, per-skill confidence, and contributing sources."""

    name: str           # canonical name, e.g. "JavaScript" not "JS"
    confidence: float   # 0.0–1.0
    sources: list[str] = field(default_factory=list)


@dataclass
class CanonicalExperience:
    """A normalized work-experience entry."""

    company: Optional[str] = None
    title: Optional[str] = None
    start: Optional[str] = None   # YYYY-MM
    end: Optional[str] = None     # YYYY-MM, or None for current role
    summary: Optional[str] = None


@dataclass
class CanonicalEducation:
    """A normalized education entry."""

    institution: Optional[str] = None
    degree: Optional[str] = None
    field: Optional[str] = None
    end_year: Optional[int] = None


@dataclass
class ProvenanceEntry:
    """Records where a field's value came from and how it was extracted."""

    field: str    # canonical field name, e.g. "phones[0]", "full_name"
    source: str   # source_name, e.g. "csv", "github"
    method: str   # extraction method: "direct_extract", "nlp_extract", "api_fetch", etc.


@dataclass
class CanonicalProfile:
    """Single, clean, merged candidate record.

    All values here are fully normalized:
    - phones: E.164 format
    - dates: YYYY-MM format
    - country: ISO-3166 alpha-2
    - skill names: canonical via alias map

    Provenance is populated for every non-null field so that every value
    is traceable to a source and extraction method.
    """

    candidate_id: str
    full_name: Optional[str] = None
    emails: list[str] = field(default_factory=list)          # deduplicated
    phones: list[str] = field(default_factory=list)          # E.164, deduplicated
    location: CanonicalLocation = field(default_factory=CanonicalLocation)
    links: CanonicalLinks = field(default_factory=CanonicalLinks)
    headline: Optional[str] = None
    years_experience: Optional[float] = None
    skills: list[CanonicalSkill] = field(default_factory=list)
    experience: list[CanonicalExperience] = field(default_factory=list)
    education: list[CanonicalEducation] = field(default_factory=list)
    provenance: list[ProvenanceEntry] = field(default_factory=list)
    overall_confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain nested dict for the projection layer.

        Uses dataclasses.asdict() for recursive conversion. The projector
        reads from this dict — it never touches the dataclass directly.
        """
        # TODO: return asdict(self) once all nested dataclasses are confirmed stable
        # TODO: Convert any non-serializable types (e.g. datetime) to strings here
        raise NotImplementedError
