"""Pipeline orchestrator — wires all stages end-to-end.

The Pipeline class is the single entry point for the transformation.
Both the CLI and any future UI call pipeline.run(). No stage module
should import from this module (it imports everything, nothing imports it
except the interface layer).

Stage order:
  1. load_alias_map()           (once per run)
  2. _ingest(inputs)            → flat list of RawRecords
  3. _normalize_all(records)    → normalizes in place
  4. group_records(records)     → list of per-person groups
  5. merger.merge(group)        → one CanonicalProfile per group
  6. score_profile(profile)     → overall_confidence populated
  7. projector.project(...)     → final output dict
"""
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
from src.normalizers.location import normalize_country
from src.normalizers.phone import normalize_phones
from src.normalizers.skills import canonicalize_skill, load_alias_map
from src.projection.config_parser import OutputConfig, default_config, load_config
from src.projection.projector import Projector
from src.scoring.confidence import score_profile

logger = logging.getLogger(__name__)


def _build_default_adapters() -> list[BaseAdapter]:
    """Construct the default ordered list of adapters.

    LinkedInAdapter before ATSJsonAdapter so that linkedin_*.json files
    are not accidentally routed to the ATS adapter.
    """
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
            inputs=["recruiter.csv", "https://github.com/octocat", "notes.txt"],
            config_path="configs/custom.json",
        )
        # results is a list of dicts, one per candidate, ready for json.dumps()
    """

    def __init__(
        self,
        adapters: Optional[list[BaseAdapter]] = None,
        github_token: Optional[str] = None,
    ) -> None:
        """Initialize the pipeline.

        Args:
            adapters: Override the default adapter list. If None, all adapters
                      are registered with defaults.
            github_token: Optional GitHub personal access token for higher
                          API rate limits.
        """
        if adapters is not None:
            self.adapters = adapters
        else:
            self.adapters = _build_default_adapters()
            # Inject token into the GitHub adapter if provided
            # TODO: Find GitHubAdapter in self.adapters and set .token = github_token

        self.merger = Merger()
        self.projector = Projector()

    def run(
        self,
        inputs: list[str],
        config_path: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Run the full pipeline on a list of input paths or URLs.

        Args:
            inputs: List of file paths or URLs. Each element is routed to
                    the first adapter whose can_handle() returns True.
            config_path: Path to a runtime output config JSON. If None,
                         the default schema (all fields) is used.

        Returns:
            List of output dicts, one per discovered candidate, ready for
            JSON serialization.
        """
        # TODO: load_alias_map()  — idempotent, safe to call every run
        # TODO: config = load_config(config_path) if config_path else default_config()
        # TODO: raw_records = self._ingest(inputs)
        # TODO: raw_records = self._normalize_all(raw_records)
        # TODO: groups = group_records(raw_records)
        # TODO: profiles: list[CanonicalProfile] = [self.merger.merge(g) for g in groups]
        # TODO: for p in profiles: p.overall_confidence = score_profile(p)
        # TODO: return [self.projector.project(p, config) for p in profiles]
        raise NotImplementedError

    def _ingest(self, inputs: list[str]) -> list[RawRecord]:
        """Route each input to the appropriate adapter and collect RawRecords.

        Inputs that no adapter can handle are logged as warnings and skipped.
        Adapter errors (caught inside load()) result in an empty list for
        that input — they do not stop the pipeline.

        Args:
            inputs: List of file paths or URLs.

        Returns:
            Flat list of all RawRecords from all successfully loaded inputs.
        """
        # TODO: records = []
        # TODO: for inp in inputs:
        #           adapter = next((a for a in self.adapters if a.can_handle(inp)), None)
        #           if adapter is None: logger.warning("No adapter for: %s — skipping", inp); continue
        #           records.extend(adapter.load(inp))
        # TODO: return records
        raise NotImplementedError

    def _normalize_all(self, records: list[RawRecord]) -> list[RawRecord]:
        """Apply all normalizers to every RawRecord, mutating fields in place.

        Normalization order:
          1. Phones → E.164
          2. Country → ISO-3166 alpha-2
          3. Skill names → canonical
          4. Experience dates → YYYY-MM (start and end)

        Date normalization for education end_year is deferred to the merger
        since it is an integer, not a string.

        Args:
            records: List of RawRecords to normalize.

        Returns:
            The same list with fields mutated in place.
        """
        # TODO: for record in records:
        #   record.phones = normalize_phones(record.phones)
        #   if record.location_country:
        #       record.location_country = normalize_country(record.location_country) or record.location_country
        #   for skill in record.skills:
        #       skill.name = canonicalize_skill(skill.name)
        #   for exp in record.experience:
        #       exp.start = normalize_date(exp.start) if exp.start else None
        #       exp.end = normalize_date(exp.end) if exp.end else None
        # TODO: return records
        raise NotImplementedError
