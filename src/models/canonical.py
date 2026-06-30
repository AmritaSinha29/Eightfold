"""Canonical profile — the clean internal record produced by the merger."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional


@dataclass
class CanonicalLocation:
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None  # ISO-3166 alpha-2


@dataclass
class CanonicalLinks:
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None
    other: list[str] = field(default_factory=list)


@dataclass
class CanonicalSkill:
    name: str
    confidence: float
    sources: list[str] = field(default_factory=list)


@dataclass
class CanonicalExperience:
    company: Optional[str] = None
    title: Optional[str] = None
    start: Optional[str] = None   # YYYY-MM
    end: Optional[str] = None     # YYYY-MM, or None for current role
    summary: Optional[str] = None


@dataclass
class CanonicalEducation:
    institution: Optional[str] = None
    degree: Optional[str] = None
    field: Optional[str] = None
    end_year: Optional[int] = None


@dataclass
class ProvenanceEntry:
    field: str
    source: str
    method: str


@dataclass
class CanonicalProfile:
    """Single, clean, merged candidate record.

    All values are fully normalized:
    - phones: E.164 format
    - dates: YYYY-MM format
    - country: ISO-3166 alpha-2
    - skill names: canonical via alias map
    """

    candidate_id: str
    full_name: Optional[str] = None
    emails: list[str] = field(default_factory=list)
    phones: list[str] = field(default_factory=list)
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
        return asdict(self)
