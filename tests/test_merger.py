"""Tests for identity matching and field-level merging."""
from __future__ import annotations

import pytest

from src.merger.conflict import SourcePriority, merge_lists, pick_winner
from src.merger.identity import group_records
from src.merger.merger import Merger
from src.models.canonical import CanonicalProfile
from src.models.raw_record import RawRecord, RawSkill


def _make_record(**kwargs) -> RawRecord:
    """Helper: build a minimal RawRecord with source_name='csv'."""
    defaults = {"source_name": "csv", "source_path": "test.csv"}
    defaults.update(kwargs)
    return RawRecord(**defaults)


class TestIdentityMatching:
    """Tests for group_records()."""

    def test_same_email_groups_records(self):
        """Two records sharing an email should land in the same group."""
        r1 = _make_record(emails=["alice@example.com"], source_name="csv")
        r2 = _make_record(emails=["alice@example.com"], source_name="notes")
        groups = group_records([r1, r2])
        assert len(groups) == 1
        assert len(groups[0]) == 2

    def test_different_emails_are_separate_candidates(self):
        """Records with no shared identifiers should form separate groups."""
        r1 = _make_record(emails=["alice@example.com"])
        r2 = _make_record(emails=["bob@example.com"])
        assert len(group_records([r1, r2])) == 2

    def test_phone_match_groups_records(self):
        """Records sharing a phone but no email should still be grouped."""
        r1 = _make_record(phones=["+15551234567"])
        r2 = _make_record(phones=["+15551234567"])
        groups = group_records([r1, r2])
        assert len(groups) == 1

    def test_fuzzy_name_match(self):
        """'Alice Johnson' and 'Alice M. Johnson' with same country → one group."""
        r1 = _make_record(full_name="Alice Johnson", location_country="US")
        r2 = _make_record(full_name="Alice M. Johnson", location_country="US")
        groups = group_records([r1, r2])
        assert len(groups) == 1

    def test_transitivity(self):
        """If A matches B and B matches C, all three should be in one group."""
        r1 = _make_record(emails=["alice@x.com"])
        r2 = _make_record(emails=["alice@x.com", "a@y.com"])
        r3 = _make_record(emails=["a@y.com"])
        groups = group_records([r1, r2, r3])
        assert len(groups) == 1


class TestConflictResolution:
    """Tests for pick_winner and merge_lists."""

    def test_unanimous_values(self):
        """All sources agree → return that value without conflict."""
        result = pick_winner([("alice", "csv"), ("alice", "notes")])
        assert result[0] == "alice"

    def test_csv_beats_notes_on_conflict(self):
        """CSV has higher priority than notes."""
        result = pick_winner([("val_notes", "notes"), ("val_csv", "csv")])
        assert result == ("val_csv", "csv")

    def test_deterministic_on_equal_priority(self):
        """Two sources at the same priority → sorted by value string."""
        result1 = pick_winner([("b_val", "resume"), ("a_val", "resume")])
        result2 = pick_winner([("a_val", "resume"), ("b_val", "resume")])
        assert result1 == result2

    def test_pick_winner_raises_on_empty(self):
        """pick_winner([]) should raise ValueError."""
        with pytest.raises(ValueError):
            pick_winner([])

    def test_merge_lists_deduplicates(self):
        """merge_lists should deduplicate values across sources."""
        result = merge_lists([
            (["a@b.com", "c@d.com"], "csv"),
            (["a@b.com"], "notes"),
        ])
        assert result == ["a@b.com", "c@d.com"]


class TestMerger:
    """Tests for Merger.merge()."""

    def test_single_record_produces_valid_profile(self):
        """A group of one record should still produce a CanonicalProfile."""
        r = _make_record(full_name="Alice Johnson", emails=["alice@example.com"])
        profile = Merger().merge([r])
        assert isinstance(profile, CanonicalProfile)
        assert profile.candidate_id is not None
        assert len(profile.candidate_id) > 0

    def test_emails_merged_and_deduplicated(self):
        """Emails from multiple sources should be merged and deduplicated."""
        r1 = _make_record(emails=["alice@x.com", "shared@x.com"])
        r2 = _make_record(emails=["shared@x.com", "bob@x.com"])
        profile = Merger().merge([r1, r2])
        assert "alice@x.com" in profile.emails
        assert "bob@x.com" in profile.emails
        assert profile.emails.count("shared@x.com") == 1

    def test_provenance_populated_for_all_fields(self):
        """Every non-null field in the output should have a provenance entry."""
        r = _make_record(full_name="Alice Johnson", emails=["alice@example.com"])
        profile = Merger().merge([r])
        assert len(profile.provenance) > 0
        fields_with_prov = {p.field for p in profile.provenance}
        assert "full_name" in fields_with_prov
        assert "emails" in fields_with_prov

    def test_candidate_id_is_deterministic(self):
        """Same email + name → same candidate_id across two separate calls."""
        r = _make_record(full_name="Alice Johnson", emails=["alice@example.com"])
        merger = Merger()
        assert merger.merge([r]).candidate_id == merger.merge([r]).candidate_id

    def test_skills_deduplicated_by_canonical_name(self):
        """Skills from multiple sources with same canonical name → one entry."""
        r1 = _make_record(skills=[RawSkill(name="Python", source_name="csv")])
        r2 = _make_record(skills=[RawSkill(name="Python", source_name="notes")])
        profile = Merger().merge([r1, r2])
        skill_names = [s.name for s in profile.skills]
        assert skill_names.count("Python") == 1
