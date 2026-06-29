"""Edge case, robustness, and integration tests.

These tests verify the pipeline's non-functional requirements:
- Determinism: same inputs → same output
- Robustness: bad inputs don't crash
- Explainability: provenance is always populated

The gold-profile test at the bottom is the primary end-to-end integration test.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.pipeline import Pipeline


class TestRobustness:
    """The pipeline must degrade gracefully — never crash on bad input."""

    def test_empty_inputs_list_returns_empty(self):
        """Pipeline.run([]) should return [] without error."""
        # TODO: assert Pipeline().run([]) == []
        pytest.skip("Not yet implemented")

    def test_nonexistent_file_is_skipped(self):
        """A path that doesn't exist should be skipped, not crash."""
        # TODO: result = Pipeline().run(["/tmp/does_not_exist.csv"])
        # TODO: assert result == []
        pytest.skip("Not yet implemented")

    def test_malformed_csv_produces_no_records(self, tmp_path: Path):
        """A corrupted CSV file should yield [] records, not an exception."""
        # TODO: Write ",,,,\x00\x01" to a .csv file
        # TODO: assert Pipeline().run([str(path)]) == []
        pytest.skip("Not yet implemented")

    def test_malformed_json_produces_no_records(self, tmp_path: Path):
        """An invalid JSON file should yield [] records, not an exception."""
        pytest.skip("Not yet implemented")

    def test_unrecognized_input_type_is_skipped(self, tmp_path: Path):
        """An input with no matching adapter should be logged and skipped."""
        # TODO: Write a .xyz file; assert pipeline runs and returns []
        pytest.skip("Not yet implemented")


class TestDeterminism:
    """Same inputs must always produce the same output."""

    def test_two_runs_produce_identical_output(self, tmp_path: Path):
        """Running the pipeline twice on the same CSV produces identical results."""
        # TODO: Write a CSV to tmp_path
        # TODO: run1 = Pipeline().run([path])
        # TODO: run2 = Pipeline().run([path])
        # TODO: assert json.dumps(run1, sort_keys=True) == json.dumps(run2, sort_keys=True)
        pytest.skip("Not yet implemented")

    def test_candidate_id_stable_across_runs(self):
        """The same email + name always produces the same candidate_id."""
        # TODO: Run merger with same inputs; assert candidate_id matches
        pytest.skip("Not yet implemented")

    def test_source_order_does_not_change_id(self, tmp_path: Path):
        """Swapping input order should not change candidate_id (it's content-based)."""
        pytest.skip("Not yet implemented")


class TestProvenance:
    """Every field in the output must be traceable."""

    def test_every_non_null_field_has_provenance(self, tmp_path: Path):
        """Running the pipeline and inspecting provenance: no non-null field is missing one."""
        pytest.skip("Not yet implemented")

    def test_conflict_reflected_in_provenance(self, tmp_path: Path):
        """When two sources conflict, the losing value still appears in provenance."""
        pytest.skip("Not yet implemented")


class TestGoldProfile:
    """Integration test: full pipeline on sample inputs vs a known-good profile.

    This test represents a complete end-to-end validation. It is the most
    important test in the suite. Fill it in after implementing the pipeline.
    """

    SAMPLE_INPUTS = [
        "sample_inputs/recruiter.csv",
        "sample_inputs/notes.txt",
    ]

    def test_alice_end_to_end_default_schema(self):
        """Full pipeline on CSV + notes should produce Alice's canonical profile.

        Covers:
        - Two source types (structured + unstructured)
        - Normalization: phone (E.164), country (ISO-3166)
        - Merge: CSV wins on full_name, emails, phones (higher priority)
        - Notes contribute skills via text_heuristic
        - Default schema: all fields present
        - Provenance: populated for at least name, email, skills
        """
        # TODO: results = Pipeline().run(self.SAMPLE_INPUTS)
        # TODO: assert len(results) == 1
        # TODO: alice = results[0]
        # TODO: assert alice["full_name"] == "Alice Johnson"
        # TODO: assert "+14155550101" in alice["phones"]
        # TODO: assert alice["location"]["country"] == "US"
        # TODO: assert any(s["name"] == "Python" for s in alice["skills"])
        # TODO: assert alice["provenance"]  # non-empty
        pytest.skip("Not yet implemented")

    def test_alice_custom_config_minimal_output(self):
        """Pipeline with example_custom_config should produce a remapped, minimal dict."""
        # TODO: results = Pipeline().run(self.SAMPLE_INPUTS, config_path="configs/example_custom_config.json")
        # TODO: alice = results[0]
        # TODO: assert "primary_email" in alice  # renamed field
        # TODO: assert "emails" not in alice     # original key absent
        # TODO: assert "candidate_id" not in alice  # not in custom config
        pytest.skip("Not yet implemented")
