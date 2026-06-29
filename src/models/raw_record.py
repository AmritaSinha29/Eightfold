"""Raw record — per-source intermediate representation before merging.

Every adapter produces one or more RawRecord objects. No normalization has
been applied at this point: dates are raw strings, phones are raw, country
names are raw. The merger and normalizer layers consume these.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class RawSkill:
    """A skill as it appeared in one source, before canonicalization."""

    name: str        # raw text, e.g. "JS", "react.js"
    source_name: str # which source produced this, e.g. "csv"


@dataclass
class RawExperience:
    """A work experience entry as extracted from one source, before normalization."""

    company: Optional[str] = None
    title: Optional[str] = None
    start: Optional[str] = None   # raw string — NOT yet YYYY-MM
    end: Optional[str] = None     # raw string — NOT yet YYYY-MM; None = current role
    summary: Optional[str] = None


@dataclass
class RawEducation:
    """An education entry as extracted from one source, before normalization."""

    institution: Optional[str] = None
    degree: Optional[str] = None
    field: Optional[str] = None
    end_year: Optional[str] = None  # raw string — NOT yet int


@dataclass
class RawRecord:
    """Intermediate representation of candidate data from a single source.

    Invariants:
    - All string values are raw (no E.164, no ISO-3166, no YYYY-MM).
    - A missing field is None, never an empty string used as a sentinel.
    - extra holds fields from the source that have no canonical mapping.
    """

    source_name: str  # e.g. "csv", "ats_json", "github", "resume", "notes", "linkedin"
    source_path: str  # file path or URL used to load this record

    # --- Identity fields ---
    full_name: Optional[str] = None
    emails: list[str] = field(default_factory=list)
    phones: list[str] = field(default_factory=list)   # raw, pre-E.164

    # --- Location (raw strings, pre-ISO normalization) ---
    location_city: Optional[str] = None
    location_region: Optional[str] = None
    location_country: Optional[str] = None

    # --- Profile links ---
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    other_links: list[str] = field(default_factory=list)

    # --- Profile fields ---
    headline: Optional[str] = None
    years_experience: Optional[float] = None  # only if explicitly stated in source

    # --- Structured sub-records ---
    skills: list[RawSkill] = field(default_factory=list)
    experience: list[RawExperience] = field(default_factory=list)
    education: list[RawEducation] = field(default_factory=list)

    # --- Unmapped fields ---
    extra: dict[str, Any] = field(default_factory=dict)
