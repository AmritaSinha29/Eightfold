"""Tests for the projection layer — config parsing, path eval, projector, validator."""
from __future__ import annotations

import pytest

from src.projection.config_parser import OutputConfig, default_config, parse_config
from src.projection.path_eval import evaluate_path
from src.projection.projector import Projector
from src.projection.validator import build_json_schema, validate_output


class TestConfigParser:
    """Tests for parse_config() and load_config()."""

    def test_parse_minimal_valid_config(self):
        """Config with only 'fields' key should parse without error."""
        # TODO: raw = {"fields": [{"path": "full_name", "type": "string"}]}
        # TODO: config = parse_config(raw)
        # TODO: assert len(config.fields) == 1
        # TODO: assert config.on_missing == "null"
        pytest.skip("Not yet implemented")

    def test_invalid_on_missing_raises(self):
        """on_missing values other than 'null'/'omit'/'error' should raise ValueError."""
        # TODO: with pytest.raises(ValueError): parse_config({"fields": [], "on_missing": "ignore"})
        pytest.skip("Not yet implemented")

    def test_field_from_path_parsed(self):
        """'from' key in a field spec should populate FieldSpec.from_path."""
        pytest.skip("Not yet implemented")

    def test_default_config_includes_all_canonical_fields(self):
        """default_config() should cover all 13 canonical schema fields."""
        # TODO: config = default_config()
        # TODO: paths = {f.path for f in config.fields}
        # TODO: assert "candidate_id" in paths and "overall_confidence" in paths
        pytest.skip("Not yet implemented")


class TestPathEval:
    """Tests for evaluate_path()."""

    def test_simple_field(self):
        """'full_name' returns the scalar value."""
        # TODO: assert evaluate_path({"full_name": "Alice"}, "full_name") == "Alice"
        pytest.skip("Not yet implemented")

    def test_indexed_field_first_element(self):
        """'emails[0]' returns the first email."""
        # TODO: assert evaluate_path({"emails": ["a@b.com", "c@d.com"]}, "emails[0]") == "a@b.com"
        pytest.skip("Not yet implemented")

    def test_indexed_field_out_of_bounds_returns_none(self):
        """'emails[99]' on a short list → None, not IndexError."""
        # TODO: assert evaluate_path({"emails": ["a@b.com"]}, "emails[99]") is None
        pytest.skip("Not yet implemented")

    def test_map_field_extracts_subfield(self):
        """'skills[].name' maps over the skills list and extracts names."""
        # TODO: data = {"skills": [{"name": "Python", "confidence": 0.9}, {"name": "Go"}]}
        # TODO: assert evaluate_path(data, "skills[].name") == ["Python", "Go"]
        pytest.skip("Not yet implemented")

    def test_missing_top_level_field_returns_none(self):
        """A path to a field that doesn't exist → None."""
        pytest.skip("Not yet implemented")

    def test_unrecognized_syntax_raises_value_error(self):
        """Path with unsupported syntax should raise ValueError."""
        # TODO: with pytest.raises(ValueError): evaluate_path({}, "skills..name")
        pytest.skip("Not yet implemented")


class TestProjector:
    """Tests for Projector.project()."""

    def test_on_missing_null_includes_field_as_none(self):
        """Missing field with on_missing='null' appears in output as None."""
        pytest.skip("Not yet implemented")

    def test_on_missing_omit_excludes_field(self):
        """Missing field with on_missing='omit' is absent from the output dict."""
        pytest.skip("Not yet implemented")

    def test_on_missing_error_raises_for_required_field(self):
        """Required missing field with on_missing='error' → ValueError."""
        pytest.skip("Not yet implemented")

    def test_field_rename_via_from_path(self):
        """'from': 'emails[0]' maps first email to the renamed output key."""
        pytest.skip("Not yet implemented")

    def test_e164_normalize_applied(self):
        """normalize='E164' on a phone field should produce E.164 output."""
        pytest.skip("Not yet implemented")


class TestValidator:
    """Tests for validate_output and build_json_schema."""

    def test_valid_output_passes(self):
        """A well-formed output dict should not raise."""
        pytest.skip("Not yet implemented")

    def test_missing_required_field_raises(self):
        """A required field absent from output → ValueError."""
        pytest.skip("Not yet implemented")

    def test_build_json_schema_structure(self):
        """build_json_schema should return a dict with 'type', 'properties', 'required'."""
        pytest.skip("Not yet implemented")
