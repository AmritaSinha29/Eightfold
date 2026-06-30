"""Tests for the projection layer — config parsing, path eval, projector, validator."""
from __future__ import annotations

import pytest

from src.projection.config_parser import FieldSpec, OutputConfig, default_config, parse_config
from src.projection.path_eval import evaluate_path
from src.projection.projector import Projector
from src.projection.validator import build_json_schema, validate_output


def _make_data(**kwargs) -> dict:
    """Minimal candidate dict for projector tests."""
    base = {
        "candidate_id": "abc123",
        "full_name": None,
        "emails": [],
        "phones": [],
        "location": {},
        "links": {},
        "headline": None,
        "years_experience": None,
        "skills": [],
        "experience": [],
        "education": [],
        "provenance": [],
        "overall_confidence": 0.0,
    }
    base.update(kwargs)
    return base


class TestConfigParser:
    def test_parse_minimal_valid_config(self):
        raw = {"fields": [{"path": "full_name", "type": "string"}]}
        config = parse_config(raw)
        assert len(config.fields) == 1
        assert config.fields[0].path == "full_name"
        assert config.on_missing == "null"

    def test_invalid_on_missing_raises(self):
        with pytest.raises(ValueError):
            parse_config({"fields": [], "on_missing": "ignore"})

    def test_field_from_path_parsed(self):
        raw = {"fields": [{"path": "primary_email", "from": "emails[0]"}]}
        config = parse_config(raw)
        assert config.fields[0].from_path == "emails[0]"
        assert config.fields[0].path == "primary_email"

    def test_default_config_includes_all_canonical_fields(self):
        config = default_config()
        paths = {f.path for f in config.fields}
        assert "candidate_id" in paths
        assert "skills" in paths
        assert "experience" in paths
        assert "education" in paths
        assert config.include_confidence is True
        assert config.include_provenance is True

    def test_missing_fields_key_raises(self):
        with pytest.raises(ValueError):
            parse_config({"on_missing": "null"})

    def test_field_spec_required_and_normalize(self):
        raw = {"fields": [{"path": "phones", "required": True, "normalize": "E164"}]}
        config = parse_config(raw)
        spec = config.fields[0]
        assert spec.required is True
        assert spec.normalize == "E164"


class TestPathEval:
    def test_simple_field(self):
        assert evaluate_path({"full_name": "Alice"}, "full_name") == "Alice"

    def test_indexed_field_first_element(self):
        assert evaluate_path({"emails": ["a@b.com", "c@d.com"]}, "emails[0]") == "a@b.com"

    def test_indexed_field_second_element(self):
        assert evaluate_path({"emails": ["a@b.com", "c@d.com"]}, "emails[1]") == "c@d.com"

    def test_indexed_field_out_of_bounds_returns_none(self):
        assert evaluate_path({"emails": ["a@b.com"]}, "emails[99]") is None

    def test_map_field_extracts_subfield(self):
        data = {"skills": [{"name": "Python", "confidence": 0.9}, {"name": "Go"}]}
        assert evaluate_path(data, "skills[].name") == ["Python", "Go"]

    def test_missing_top_level_field_returns_none(self):
        assert evaluate_path({}, "full_name") is None

    def test_unrecognized_syntax_raises_value_error(self):
        with pytest.raises(ValueError):
            evaluate_path({}, "skills..name")

    def test_indexed_subfield(self):
        data = {"experience": [{"company": "Acme", "title": "Eng"}, {"company": "Beta"}]}
        assert evaluate_path(data, "experience[0].company") == "Acme"

    def test_indexed_subfield_missing_key_returns_none(self):
        data = {"experience": [{"company": "Acme"}]}
        assert evaluate_path(data, "experience[0].title") is None


class TestProjector:
    def _projector(self):
        return Projector()

    def test_on_missing_null_includes_field_as_none(self):
        config = OutputConfig(
            fields=[FieldSpec(path="full_name", type="string")],
            on_missing="null",
        )
        result = self._projector().project(_make_data(), config)
        assert "full_name" in result
        assert result["full_name"] is None

    def test_on_missing_omit_excludes_field(self):
        config = OutputConfig(
            fields=[FieldSpec(path="full_name", type="string")],
            on_missing="omit",
        )
        result = self._projector().project(_make_data(), config)
        assert "full_name" not in result

    def test_on_missing_error_raises_for_required_field(self):
        config = OutputConfig(
            fields=[FieldSpec(path="full_name", required=True)],
            on_missing="error",
        )
        with pytest.raises(ValueError, match="Required field"):
            self._projector().project(_make_data(), config)

    def test_field_rename_via_from_path(self):
        data = _make_data(emails=["alice@example.com", "work@example.com"])
        config = OutputConfig(
            fields=[FieldSpec(path="primary_email", from_path="emails[0]")],
            on_missing="null",
        )
        result = self._projector().project(data, config)
        assert result["primary_email"] == "alice@example.com"

    def test_e164_normalize_applied(self):
        from src.normalizers.skills import load_alias_map
        load_alias_map()
        data = _make_data(phones=["+14155550101"])
        config = OutputConfig(
            fields=[FieldSpec(path="phones", normalize="E164")],
            on_missing="null",
        )
        result = self._projector().project(data, config)
        assert result["phones"] == ["+14155550101"]

    def test_include_confidence_appended(self):
        config = OutputConfig(fields=[], include_confidence=True)
        result = self._projector().project(_make_data(overall_confidence=0.85), config)
        assert result["overall_confidence"] == pytest.approx(0.85)

    def test_include_provenance_appended(self):
        prov = [{"field": "full_name", "source": "csv", "method": "direct"}]
        config = OutputConfig(fields=[], include_provenance=True)
        result = self._projector().project(_make_data(provenance=prov), config)
        assert result["provenance"] == prov

    def test_project_does_not_import_canonical_profile(self):
        """Projector.project() must accept a plain dict, not a CanonicalProfile."""
        import inspect
        import src.projection.projector as mod
        source = inspect.getsource(mod)
        assert "CanonicalProfile" not in source

    def test_scalar_field_passed_through(self):
        data = _make_data(full_name="Alice Johnson", years_experience=5.8)
        config = OutputConfig(
            fields=[
                FieldSpec(path="full_name", type="string"),
                FieldSpec(path="years_experience", type="number"),
            ],
            on_missing="null",
        )
        result = self._projector().project(data, config)
        assert result["full_name"] == "Alice Johnson"
        assert result["years_experience"] == pytest.approx(5.8)


class TestValidator:
    def test_valid_output_passes(self):
        config = OutputConfig(fields=[FieldSpec(path="full_name", type="string")])
        validate_output({"full_name": "Alice"}, config)  # must not raise

    def test_missing_required_field_raises(self):
        config = OutputConfig(fields=[FieldSpec(path="candidate_id", type="string", required=True)])
        with pytest.raises(ValueError, match="Output validation failed"):
            validate_output({}, config)

    def test_build_json_schema_structure(self):
        config = OutputConfig(
            fields=[
                FieldSpec(path="candidate_id", type="string", required=True),
                FieldSpec(path="full_name", type="string"),
            ]
        )
        schema = build_json_schema(config)
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema
        assert "candidate_id" in schema["required"]
        assert "full_name" not in schema["required"]

    def test_nullable_optional_field_passes(self):
        """Optional fields should accept null values (on_missing='null' path)."""
        config = OutputConfig(fields=[FieldSpec(path="headline", type="string")])
        validate_output({"headline": None}, config)  # must not raise

    def test_type_mismatch_raises(self):
        config = OutputConfig(fields=[FieldSpec(path="years_experience", type="number", required=True)])
        with pytest.raises(ValueError, match="Output validation failed"):
            validate_output({"years_experience": "five"}, config)
