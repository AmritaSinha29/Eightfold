"""Tests for identity matching and field-level merging."""
from __future__ import annotations

import pytest

from src.merger.conflict import SourcePriority, merge_lists, pick_winner
from src.merger.identity import group_records
from src.merger.merger import Merger
from src.models.raw_record import RawRecord


def _make_record(**kwargs) -> RawRecord:
    """Helper: build a minimal RawRecord with source_name='csv'."""
    defaults = {"source_name": "csv", "source_path": "test.csv"}
    defaults.update(kwargs)
    return RawRecord(**defaults)


class TestIdentityMatching:
    """Tests for group_records()."""

    def test_same_email_groups_records(self):
        """Two records sharing an email should land in the same group."""
        # TODO: r1 = _make_record(emails=["alice@example.com"], source_name="csv")
        # TODO: r2 = _make_record(emails=["alice@example.com"], source_name="notes")
        # TODO: groups = group_records([r1, r2])
        # TODO: assert len(groups) == 1 and len(groups[0]) == 2
        pytest.skip("Not yet implemented")

    def test_different_emails_are_separate_candidates(self):
        """Records with no shared identifiers should form separate groups."""
        # TODO: r1, r2 = distinct records with different emails
        # TODO: assert len(group_records([r1, r2])) == 2
        pytest.skip("Not yet implemented")

    def test_phone_match_groups_records(self):
        """Records sharing a phone but no email should still be grouped."""
        pytest.skip("Not yet implemented")

    def test_fuzzy_name_match(self):
        """'Alice Johnson' and 'Alice M. Johnson' with same country → one group."""
        pytest.skip("Not yet implemented")

    def test_transitivity(self):
        """If A matches B and B matches C, all three should be in one group."""
        pytest.skip("Not yet implemented")


class TestConflictResolution:
    """Tests for pick_winner and merge_lists."""

    def test_unanimous_values(self):
        """All sources agree → return that value without conflict."""
        # TODO: result = pick_winner([("alice", "csv"), ("alice", "notes")])
        # TODO: assert result[0] == "alice"
        pytest.skip("Not yet implemented")

    def test_csv_beats_notes_on_conflict(self):
        """CSV has higher priority than notes."""
        # TODO: result = pick_winner([("val_notes", "notes"), ("val_csv", "csv")])
        # TODO: assert result == ("val_csv", "csv")
        pytest.skip("Not yet implemented")

    def test_deterministic_on_equal_priority(self):
        """Two sources at the same priority → sorted by value string."""
        pytest.skip("Not yet implemented")

    def test_pick_winner_raises_on_empty(self):
        """pick_winner([]) should raise ValueError."""
        # TODO: with pytest.raises(ValueError): pick_winner([])
        pytest.skip("Not yet implemented")

    def test_merge_lists_deduplicates(self):
        """merge_lists should deduplicate values across sources."""
        # TODO: result = merge_lists([
        #     (["a@b.com", "c@d.com"], "csv"),
        #     (["a@b.com"], "notes"),
        # ])
        # TODO: assert result == ["a@b.com", "c@d.com"]
        pytest.skip("Not yet implemented")


class TestMerger:
    """Tests for Merger.merge()."""

    def test_single_record_produces_valid_profile(self):
        """A group of one record should still produce a CanonicalProfile."""
        pytest.skip("Not yet implemented")

    def test_emails_merged_and_deduplicated(self):
        """Emails from multiple sources should be merged and deduplicated."""
        pytest.skip("Not yet implemented")

    def test_provenance_populated_for_all_fields(self):
        """Every non-null field in the output should have a provenance entry."""
        pytest.skip("Not yet implemented")

    def test_candidate_id_is_deterministic(self):
        """Same email + name → same candidate_id across two separate calls."""
        pytest.skip("Not yet implemented")

    def test_skills_deduplicated_by_canonical_name(self):
        """Skills from multiple sources with same canonical name → one entry."""
        pytest.skip("Not yet implemented")
