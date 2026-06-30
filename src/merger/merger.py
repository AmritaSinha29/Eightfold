"""Core merger — combines a group of same-person RawRecords into one CanonicalProfile."""
from __future__ import annotations

import hashlib
import uuid
from typing import Optional

from rapidfuzz import fuzz

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
from src.models.raw_record import RawEducation, RawExperience, RawRecord


class Merger:
    """Produces one CanonicalProfile from a group of same-person RawRecords."""

    def merge(self, group: list[RawRecord]) -> CanonicalProfile:
        full_name, name_prov     = self._merge_scalar("full_name", group, "full_name")
        emails,    email_prov    = self._merge_emails(group)
        phones,    phone_prov    = self._merge_phones(group)
        location,  loc_prov      = self._merge_location(group)
        links,     link_prov     = self._merge_links(group)
        headline,  head_prov     = self._merge_scalar("headline", group, "headline")
        years_exp, yrs_prov      = self._merge_scalar("years_experience", group, "years_experience")
        skills,    skill_prov    = self._merge_skills(group)
        experience               = self._merge_experience(group)
        education                = self._merge_education(group)

        # If no source explicitly stated years_experience, compute from merged dates.
        if years_exp is None and experience:
            from src.normalizers.date import compute_years_experience
            years_exp = compute_years_experience(
                [{"start": e.start, "end": e.end} for e in experience]
            )

        provenance = (
            name_prov + email_prov + phone_prov + loc_prov
            + link_prov + head_prov + yrs_prov + skill_prov
        )

        return CanonicalProfile(
            candidate_id=self._generate_id(emails[0] if emails else None, full_name),
            full_name=full_name,
            emails=emails,
            phones=phones,
            location=location,
            links=links,
            headline=headline,
            years_experience=float(years_exp) if years_exp is not None else None,
            skills=skills,
            experience=experience,
            education=education,
            provenance=provenance,
        )

    # ------------------------------------------------------------------ #
    #  Identity
    # ------------------------------------------------------------------ #

    def _generate_id(self, primary_email: Optional[str], full_name: Optional[str]) -> str:
        if primary_email or full_name:
            key = f"{(primary_email or '').lower()}|{(full_name or '').lower()}"
            return hashlib.sha256(key.encode()).hexdigest()[:16]
        return uuid.uuid4().hex[:16]

    # ------------------------------------------------------------------ #
    #  Scalar fields
    # ------------------------------------------------------------------ #

    def _merge_scalar(
        self,
        field_name: str,
        group: list[RawRecord],
        attr: str,
    ) -> tuple[Optional[Any], list[ProvenanceEntry]]:
        candidates = [
            (getattr(rec, attr), rec.source_name)
            for rec in group
            if getattr(rec, attr) is not None
        ]
        if not candidates:
            return (None, [])
        winner_val, winner_src = pick_winner(candidates)
        prov = ProvenanceEntry(field=field_name, source=winner_src, method="direct_extract")
        return (winner_val, [prov])

    # ------------------------------------------------------------------ #
    #  List fields
    # ------------------------------------------------------------------ #

    def _merge_emails(self, group: list[RawRecord]) -> tuple[list[str], list[ProvenanceEntry]]:
        items = [(rec.emails, rec.source_name) for rec in group]
        merged = merge_lists(items)
        prov = [
            ProvenanceEntry(field="emails", source=src, method="direct_extract")
            for lst, src in items
            if lst
        ]
        return (merged, prov)

    def _merge_phones(self, group: list[RawRecord]) -> tuple[list[str], list[ProvenanceEntry]]:
        items = [(rec.phones, rec.source_name) for rec in group]
        merged = merge_lists(items)
        prov = [
            ProvenanceEntry(field="phones", source=src, method="direct_extract")
            for lst, src in items
            if lst
        ]
        return (merged, prov)

    # ------------------------------------------------------------------ #
    #  Structured sub-fields
    # ------------------------------------------------------------------ #

    def _merge_location(self, group: list[RawRecord]) -> tuple[CanonicalLocation, list[ProvenanceEntry]]:
        city,    city_prov    = self._merge_scalar("location.city",    group, "location_city")
        region,  region_prov  = self._merge_scalar("location.region",  group, "location_region")
        country, country_prov = self._merge_scalar("location.country", group, "location_country")
        return (
            CanonicalLocation(city=city, region=region, country=country),
            city_prov + region_prov + country_prov,
        )

    def _merge_links(self, group: list[RawRecord]) -> tuple[CanonicalLinks, list[ProvenanceEntry]]:
        linkedin,  li_prov = self._merge_scalar("links.linkedin",  group, "linkedin_url")
        github,    gh_prov = self._merge_scalar("links.github",    group, "github_url")
        portfolio, pf_prov = self._merge_scalar("links.portfolio", group, "portfolio_url")
        other = merge_lists([(rec.other_links, rec.source_name) for rec in group])
        return (
            CanonicalLinks(linkedin=linkedin, github=github, portfolio=portfolio, other=other),
            li_prov + gh_prov + pf_prov,
        )

    def _merge_skills(
        self, group: list[RawRecord]
    ) -> tuple[list[CanonicalSkill], list[ProvenanceEntry]]:
        from src.scoring.confidence import score_skill

        skill_sources: dict[str, list[str]] = {}
        for rec in group:
            for skill in rec.skills:
                skill_sources.setdefault(skill.name, []).append(rec.source_name)

        total = len(group)
        skills = [
            CanonicalSkill(
                name=name,
                confidence=score_skill(len(sources), total),
                sources=list(dict.fromkeys(sources)),
            )
            for name, sources in skill_sources.items()
        ]
        skills.sort(key=lambda s: s.confidence, reverse=True)

        prov = [
            ProvenanceEntry(
                field=f"skills[{i}]",
                source=s.sources[0],
                method="direct_extract",
            )
            for i, s in enumerate(skills)
        ]
        return (skills, prov)

    def _merge_experience(self, group: list[RawRecord]) -> list[CanonicalExperience]:
        all_exp = [exp for rec in group for exp in rec.experience]
        merged: list[RawExperience] = []

        for exp in all_exp:
            duplicate_idx = next(
                (
                    i for i, existing in enumerate(merged)
                    if exp.company and existing.company
                    and exp.title and existing.title
                    and fuzz.token_set_ratio(
                        f"{exp.company} {exp.title}",
                        f"{existing.company} {existing.title}",
                    ) >= 80
                ),
                None,
            )
            if duplicate_idx is not None:
                existing = merged[duplicate_idx]
                fields_new = sum(1 for v in [exp.company, exp.title, exp.start, exp.end, exp.summary] if v)
                fields_old = sum(1 for v in [existing.company, existing.title, existing.start, existing.end, existing.summary] if v)
                if fields_new > fields_old:
                    merged[duplicate_idx] = exp
            else:
                merged.append(exp)

        def _sort_key(e: RawExperience) -> int:
            if e.start:
                try:
                    y, m = map(int, e.start.split("-"))
                    return -(y * 12 + m)
                except (ValueError, AttributeError):
                    pass
            return 0

        merged.sort(key=_sort_key)
        return [
            CanonicalExperience(
                company=e.company,
                title=e.title,
                start=e.start,
                end=e.end,
                summary=e.summary,
            )
            for e in merged
        ]

    def _merge_education(self, group: list[RawRecord]) -> list[CanonicalEducation]:
        all_edu = [edu for rec in group for edu in rec.education]
        merged: list[RawEducation] = []

        for edu in all_edu:
            duplicate_idx = next(
                (
                    i for i, existing in enumerate(merged)
                    if edu.institution and existing.institution
                    and fuzz.token_set_ratio(edu.institution, existing.institution) >= 80
                ),
                None,
            )
            if duplicate_idx is not None:
                existing = merged[duplicate_idx]
                fields_new = sum(1 for v in [edu.institution, edu.degree, edu.field, edu.end_year] if v)
                fields_old = sum(1 for v in [existing.institution, existing.degree, existing.field, existing.end_year] if v)
                if fields_new > fields_old:
                    merged[duplicate_idx] = edu
            else:
                merged.append(edu)

        def _year(e: RawEducation) -> int:
            if e.end_year:
                try:
                    return -int(e.end_year)
                except (ValueError, TypeError):
                    pass
            return 0

        merged.sort(key=_year)
        return [
            CanonicalEducation(
                institution=e.institution,
                degree=e.degree,
                field=e.field,
                end_year=int(e.end_year) if e.end_year and str(e.end_year).isdigit() else None,
            )
            for e in merged
        ]


# Type alias used in _merge_scalar return annotation
from typing import Any  # noqa: E402 — kept at bottom to avoid circular at module level
