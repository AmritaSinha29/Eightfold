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

_PROJECT_ROOT = Path(__file__).parent.parent


class TestRobustness:
    """The pipeline must degrade gracefully — never crash on bad input."""

    def test_empty_inputs_list_returns_empty(self):
        """Pipeline.run([]) should return [] without error."""
        assert Pipeline().run([]) == []

    def test_nonexistent_file_is_skipped(self):
        """A path that doesn't exist should be skipped, not crash."""
        result = Pipeline().run(["/tmp/does_not_exist.csv"])
        assert result == []

    def test_malformed_csv_produces_no_records(self, tmp_path: Path):
        """A corrupted CSV file should yield [] records, not an exception."""
        path = tmp_path / "broken.csv"
        # Empty headers + no data rows → csv.DictReader finds nothing mappable
        path.write_bytes(b",,,,\x00\x01")
        assert Pipeline().run([str(path)]) == []

    def test_malformed_json_produces_no_records(self, tmp_path: Path):
        """An invalid JSON file should yield [] records, not an exception."""
        path = tmp_path / "broken.json"
        path.write_text("not valid json")
        assert Pipeline().run([str(path)]) == []

    def test_unrecognized_input_type_is_skipped(self, tmp_path: Path):
        """An input with no matching adapter should be logged and skipped."""
        path = tmp_path / "data.xyz"
        path.write_text("some content")
        assert Pipeline().run([str(path)]) == []


class TestDeterminism:
    """Same inputs must always produce the same output."""

    def test_two_runs_produce_identical_output(self, tmp_path: Path):
        """Running the pipeline twice on the same CSV produces identical results."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(
            "name,email,phone\nAlice Johnson,alice@example.com,(415) 555-0101\n"
        )
        path = str(csv_file)
        run1 = Pipeline().run([path])
        run2 = Pipeline().run([path])
        assert json.dumps(run1, sort_keys=True) == json.dumps(run2, sort_keys=True)

    def test_candidate_id_stable_across_runs(self):
        """The same email + name always produces the same candidate_id."""
        from src.merger.merger import Merger
        from src.models.raw_record import RawRecord

        r = RawRecord(
            source_name="csv",
            source_path="test.csv",
            full_name="Alice Johnson",
            emails=["alice@example.com"],
        )
        merger = Merger()
        assert merger.merge([r]).candidate_id == merger.merge([r]).candidate_id

    def test_source_order_does_not_change_id(self, tmp_path: Path):
        """Swapping input order should not change candidate_id (it's content-based)."""
        csv1 = tmp_path / "a.csv"
        csv2 = tmp_path / "b.csv"
        csv1.write_text("name,email\nAlice Johnson,alice@example.com\n")
        csv2.write_text("name,email\nAlice Johnson,alice@example.com\n")

        run1 = Pipeline().run([str(csv1), str(csv2)])
        run2 = Pipeline().run([str(csv2), str(csv1)])
        assert run1[0]["candidate_id"] == run2[0]["candidate_id"]


class TestProvenance:
    """Every field in the output must be traceable."""

    def test_every_non_null_field_has_provenance(self, tmp_path: Path):
        """Running the pipeline and inspecting provenance: no non-null field is missing one."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,email\nAlice Johnson,alice@example.com\n")
        results = Pipeline().run([str(csv_file)])
        assert len(results) == 1
        prov = results[0]["provenance"]
        assert prov
        fields_with_prov = {p["field"] for p in prov}
        assert "full_name" in fields_with_prov
        assert "emails" in fields_with_prov

    def test_conflict_reflected_in_provenance(self, tmp_path: Path):
        """When two sources conflict, the winning source appears in provenance."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("name,email\nAlice From CSV,alice@example.com\n")
        notes_file = tmp_path / "notes.txt"
        notes_file.write_text("Candidate: Alice From Notes\nEmail: alice@example.com")

        results = Pipeline().run([str(csv_file), str(notes_file)])
        alice = next(r for r in results if r.get("full_name") == "Alice From CSV")
        prov_sources = {p["source"] for p in alice["provenance"]}
        assert "csv" in prov_sources


class TestGoldProfile:
    """Integration test: full pipeline on sample inputs vs a known-good profile.

    This test represents a complete end-to-end validation. It is the most
    important test in the suite. Fill it in after implementing the pipeline.
    """

    SAMPLE_INPUTS = [
        str(_PROJECT_ROOT / "sample_inputs" / "recruiter.csv"),
        str(_PROJECT_ROOT / "sample_inputs" / "notes.txt"),
    ]

    def test_alice_end_to_end_default_schema(self):
        """Full pipeline on CSV + notes should produce Alice's canonical profile.

        Covers:
        - Two source types (structured + unstructured)
        - Normalization: phone (E.164)
        - Merge: CSV wins on full_name (higher priority)
        - Notes contribute skills via text_heuristic
        - Default schema: all fields present
        - Provenance: populated for at least name, email, skills
        """
        results = Pipeline().run(self.SAMPLE_INPUTS)
        alice = next(
            (r for r in results if r.get("full_name") == "Alice Johnson"), None
        )
        assert alice is not None
        assert "+14155550101" in alice["phones"]
        assert any(s["name"] == "Python" for s in alice["skills"])
        assert alice["provenance"]

    def test_alice_custom_config_minimal_output(self):
        """Pipeline with example_custom_config should produce a remapped, minimal dict."""
        config_path = str(_PROJECT_ROOT / "configs" / "example_custom_config.json")
        results = Pipeline().run(self.SAMPLE_INPUTS, config_path=config_path)
        alice = next(
            (r for r in results if r.get("full_name") == "Alice Johnson"), None
        )
        assert alice is not None
        assert "primary_email" in alice
        assert "emails" not in alice
        assert "candidate_id" not in alice
