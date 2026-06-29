"""Core merger — combines a group of same-person RawRecords into one CanonicalProfile.

The Merger reads already-normalized RawRecords (phones are E.164, dates are
YYYY-MM, countries are ISO-3166, skill names are canonical) and produces a
single CanonicalProfile with provenance entries for every non-null field.
"""
from __future__ import annotations

import hashlib
import uuid
from typing import Optional

from src.merger.conflict import merge_lists, pick_winner
from src.models.canonical import (
    CanonicalEducation,
    CanonicalExperience,
    CanonicalLinks,
    CanonicalLocation,
    CanonicalProfile,
    CanonicalSkill,
    ProvenanceEntry,
)
from src.models.raw_record import RawRecord


class Merger:
    """Produces one CanonicalProfile from a group of same-person RawRecords."""

    def merge(self, group: list[RawRecord]) -> CanonicalProfile:
        """Merge a non-empty group into one CanonicalProfile.

        Each field is merged independently. Provenance is recorded for every
        non-null field so that every value is traceable to a source.

        Args:
            group: Non-empty list of RawRecords all belonging to one person.

        Returns:
            A fully populated CanonicalProfile.
        """
        # TODO: Call all _merge_* helpers
        # TODO: Assemble CanonicalProfile(candidate_id=..., full_name=..., ...)
        # TODO: Return the assembled profile
        raise NotImplementedError

    # ------------------------------------------------------------------ #
    #  Identity
    # ------------------------------------------------------------------ #

    def _generate_id(
        self,
        primary_email: Optional[str],
        full_name: Optional[str],
    ) -> str:
        """Generate a deterministic candidate_id from email + name.

        Strategy: sha256(normalized_email + "|" + normalized_name)[:16].
        Falls back to uuid4 hex if both are None.

        Args:
            primary_email: First normalized email address, or None.
            full_name: Normalized full name, or None.

        Returns:
            16-character hex string (or 32-character UUID hex as fallback).
        """
        # TODO: If primary_email or full_name:
        #   key = f"{(primary_email or '').lower()}|{(full_name or '').lower()}"
        #   return hashlib.sha256(key.encode()).hexdigest()[:16]
        # TODO: return uuid.uuid4().hex[:16]
        raise NotImplementedError

    # ------------------------------------------------------------------ #
    #  Scalar fields
    # ------------------------------------------------------------------ #

    def _merge_scalar(
        self,
        field_name: str,
        group: list[RawRecord],
        attr: str,
    ) -> tuple[Optional[str], list[ProvenanceEntry]]:
        """Merge a scalar string field across the group.

        Collects non-None values from all records, resolves conflicts via
        pick_winner, and builds a ProvenanceEntry for the winning value.

        Args:
            field_name: Canonical field name for provenance (e.g. "full_name").
            group: The group of RawRecords.
            attr: The attribute name on RawRecord to read (e.g. "full_name").

        Returns:
            (winning_value_or_None, list_of_ProvenanceEntry)
        """
        # TODO: candidates = [(getattr(rec, attr), rec.source_name) for rec in group if getattr(rec, attr) is not None]
        # TODO: if not candidates: return (None, [])
        # TODO: winner_val, winner_src = pick_winner(candidates)
        # TODO: prov = ProvenanceEntry(field=field_name, source=winner_src, method="direct_extract")
        # TODO: return (winner_val, [prov])
        raise NotImplementedError

    # ------------------------------------------------------------------ #
    #  List fields
    # ------------------------------------------------------------------ #

    def _merge_emails(
        self, group: list[RawRecord]
    ) -> tuple[list[str], list[ProvenanceEntry]]:
        """Merge and deduplicate email lists across all sources.

        Args:
            group: The group of RawRecords.

        Returns:
            (deduplicated_emails, provenance_entries)
        """
        # TODO: items = [(rec.emails, rec.source_name) for rec in group]
        # TODO: merged = merge_lists(items)
        # TODO: prov = [ProvenanceEntry("emails", src, "direct_extract") for _, src in items if _]
        raise NotImplementedError

    def _merge_phones(
        self, group: list[RawRecord]
    ) -> tuple[list[str], list[ProvenanceEntry]]:
        """Merge and deduplicate phone lists (already in E.164).

        Args:
            group: The group of RawRecords.
        """
        # TODO: Same pattern as _merge_emails
        raise NotImplementedError

    # ------------------------------------------------------------------ #
    #  Structured sub-fields
    # ------------------------------------------------------------------ #

    def _merge_location(
        self, group: list[RawRecord]
    ) -> tuple[CanonicalLocation, list[ProvenanceEntry]]:
        """Merge location sub-fields (city, region, country) independently.

        Args:
            group: The group of RawRecords.
        """
        # TODO: _merge_scalar("location.city", group, "location_city")
        # TODO: _merge_scalar("location.region", group, "location_region")
        # TODO: _merge_scalar("location.country", group, "location_country")
        # TODO: Assemble CanonicalLocation
        raise NotImplementedError

    def _merge_links(
        self, group: list[RawRecord]
    ) -> tuple[CanonicalLinks, list[ProvenanceEntry]]:
        """Merge link fields.

        Args:
            group: The group of RawRecords.
        """
        # TODO: _merge_scalar for linkedin_url, github_url, portfolio_url
        # TODO: merge_lists for other_links
        # TODO: Assemble CanonicalLinks
        raise NotImplementedError

    def _merge_skills(
        self, group: list[RawRecord]
    ) -> tuple[list[CanonicalSkill], list[ProvenanceEntry]]:
        """Merge skills from all sources and compute per-skill confidence.

        Skills with the same canonical name from different sources are
        merged into one CanonicalSkill; corroboration increases confidence.

        Args:
            group: The group of RawRecords.
        """
        # TODO: Collect all (canonical_skill_name, source_name) pairs
        # TODO: Group by canonical name → {name: [sources]}
        # TODO: CanonicalSkill(name=n, confidence=score_skill(len(srcs), len(group)), sources=srcs)
        # TODO: Return sorted list (by confidence desc)
        raise NotImplementedError

    def _merge_experience(self, group: list[RawRecord]) -> list[CanonicalExperience]:
        """Merge experience entries from all sources.

        Strategy: collect all RawExperience entries, deduplicate by
        approximate (company, title) match using rapidfuzz, keeping
        the richer entry when duplicates are found.

        Args:
            group: The group of RawRecords.
        """
        # TODO: Flatten all rec.experience for rec in group
        # TODO: Deduplicate: if two entries share company+title (fuzzy >= 80): keep the one with more fields set
        # TODO: Sort by start date descending (most recent first)
        # TODO: Convert to CanonicalExperience
        raise NotImplementedError

    def _merge_education(self, group: list[RawRecord]) -> list[CanonicalEducation]:
        """Merge education entries from all sources.

        Same strategy as _merge_experience.

        Args:
            group: The group of RawRecords.
        """
        # TODO: Same dedup pattern as _merge_experience
        # TODO: Sort by end_year descending
        # TODO: Convert to CanonicalEducation
        raise NotImplementedError
