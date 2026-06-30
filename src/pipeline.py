"""Pipeline orchestrator — wires all stages end-to-end."""
from __future__ import annotations

import logging
from typing import Any, Optional

from src.adapters.ats_json_adapter import ATSJsonAdapter
from src.adapters.base import BaseAdapter
from src.adapters.csv_adapter import CSVAdapter
from src.adapters.github_adapter import GitHubAdapter
from src.adapters.linkedin_adapter import LinkedInAdapter
from src.adapters.notes_adapter import NotesAdapter
from src.adapters.resume_adapter import ResumeAdapter
from src.merger.identity import group_records
from src.merger.merger import Merger
from src.models.canonical import CanonicalProfile
from src.models.raw_record import RawRecord
from src.normalizers.date import normalize_date
from src.normalizers.location import normalize_country
from src.normalizers.phone import normalize_phones
from src.normalizers.skills import canonicalize_skill, load_alias_map
from src.projection.config_parser import OutputConfig, default_config, load_config
from src.projection.projector import Projector
from src.scoring.confidence import score_profile

logger = logging.getLogger(__name__)


def _build_default_adapters() -> list[BaseAdapter]:
    # LinkedInAdapter must come before ATSJsonAdapter so linkedin_*.json is
    # not accidentally routed to the ATS adapter.
    return [
        CSVAdapter(),
        LinkedInAdapter(),
        ATSJsonAdapter(),
        GitHubAdapter(),
        ResumeAdapter(),
        NotesAdapter(),
    ]


class Pipeline:
    """End-to-end candidate data transformation pipeline.

    Usage::

        pipeline = Pipeline()
        results = pipeline.run(
            inputs=["recruiter.csv", "linkedin_export.json", "notes.txt"],
            config_path="configs/custom.json",
        )
    """

    def __init__(
        self,
        adapters: Optional[list[BaseAdapter]] = None,
        github_token: Optional[str] = None,
    ) -> None:
        if adapters is not None:
            self.adapters = adapters
        else:
            self.adapters = _build_default_adapters()
            if github_token:
                for adapter in self.adapters:
                    if isinstance(adapter, GitHubAdapter):
                        adapter.token = github_token
                        break

        self.merger = Merger()
        self.projector = Projector()

    def run(
        self,
        inputs: list[str],
        config_path: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Run the full pipeline and return one output dict per discovered candidate."""
        load_alias_map()
        config = load_config(config_path) if config_path else default_config()

        raw_records = self._ingest(inputs)
        raw_records = self._normalize_all(raw_records)
        groups = group_records(raw_records)

        profiles: list[CanonicalProfile] = [self.merger.merge(g) for g in groups]
        for profile in profiles:
            profile.overall_confidence = score_profile(profile)

        return [self.projector.project(p.to_dict(), config) for p in profiles]

    def _ingest(self, inputs: list[str]) -> list[RawRecord]:
        records: list[RawRecord] = []
        for inp in inputs:
            adapter = next((a for a in self.adapters if a.can_handle(inp)), None)
            if adapter is None:
                logger.warning("No adapter found for input: %s — skipping", inp)
                continue
            records.extend(adapter.load(inp))
        return records

    def _normalize_all(self, records: list[RawRecord]) -> list[RawRecord]:
        for record in records:
            record.phones = normalize_phones(record.phones)

            if record.location_country:
                record.location_country = (
                    normalize_country(record.location_country) or record.location_country
                )

            for skill in record.skills:
                skill.name = canonicalize_skill(skill.name)

            for exp in record.experience:
                exp.start = normalize_date(exp.start) if exp.start else None
                exp.end   = normalize_date(exp.end)   if exp.end   else None

        return records
