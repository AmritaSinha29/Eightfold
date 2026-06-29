"""Projection layer — reshapes a CanonicalProfile into the requested output shape.

This module is the boundary between the internal canonical record and the
external JSON output. It:
  1. Calls CanonicalProfile.to_dict() to get a plain dict.
  2. For each FieldSpec in the config, resolves the value via path_eval.
  3. Applies per-field normalization if specified.
  4. Handles missing values per config.on_missing.
  5. Attaches confidence and provenance if configured.
  6. Delegates final validation to the validator module.
"""
from __future__ import annotations

from typing import Any, Optional

from src.models.canonical import CanonicalProfile
from src.projection.config_parser import FieldSpec, OutputConfig
from src.projection.path_eval import evaluate_path
from src.projection.validator import validate_output


class Projector:
    """Applies an OutputConfig to a CanonicalProfile and returns a serializable dict."""

    def project(
        self,
        profile: CanonicalProfile,
        config: OutputConfig,
    ) -> dict[str, Any]:
        """Reshape a CanonicalProfile into a final output dict per config.

        Args:
            profile: The merged and scored canonical profile.
            config: Parsed runtime output configuration.

        Returns:
            Dict ready for json.dumps(). Keys and shape match config.fields.

        Raises:
            ValueError: If on_missing="error" and a required field is absent.
        """
        # TODO: data = profile.to_dict()
        # TODO: result = {}
        # TODO: for spec in config.fields: key, val = _apply_field(data, spec, config); handle omit
        # TODO: if config.include_confidence: result["overall_confidence"] = profile.overall_confidence
        # TODO: if config.include_provenance: result["provenance"] = [asdict(p) for p in profile.provenance]
        # TODO: validate_output(result, config)
        # TODO: return result
        raise NotImplementedError

    def _apply_field(
        self,
        data: dict[str, Any],
        spec: FieldSpec,
        config: OutputConfig,
    ) -> tuple[str, Any]:
        """Resolve and apply a single FieldSpec against the profile data dict.

        Args:
            data: Dict form of the CanonicalProfile.
            spec: The field specification from the config.
            config: Full config (for on_missing behavior).

        Returns:
            (output_key, output_value) pair.

        Raises:
            ValueError: If spec.required, value is None, and on_missing="error".
        """
        # TODO: path = spec.from_path if spec.from_path else spec.path
        # TODO: value = evaluate_path(data, path)
        # TODO: if value is None:
        #           if config.on_missing == "error" and spec.required:
        #               raise ValueError(f"Required field '{spec.path}' is missing")
        #           if config.on_missing == "omit":
        #               return (spec.path, _OMIT_SENTINEL)
        #           value = None  # on_missing == "null"
        # TODO: value = _apply_normalize(value, spec.normalize)
        # TODO: return (spec.path, value)
        raise NotImplementedError

    def _apply_normalize(self, value: Any, normalize: Optional[str]) -> Any:
        """Apply a named normalization to a resolved value.

        Supported normalize tokens:
          - "E164"      → normalize_phone(value)
          - "canonical" → canonicalize_skill(value) or canonicalize_skills(value)

        Args:
            value: The resolved value from path_eval.
            normalize: The normalization token from FieldSpec, or None.

        Returns:
            Normalized value, or the original if normalize is None or unknown.
        """
        # TODO: if normalize is None: return value
        # TODO: if normalize == "E164": normalize_phone(value) for scalar; list version for lists
        # TODO: if normalize == "canonical": canonicalize_skill(value) for scalar; list for list
        # TODO: Unknown normalize tokens: log warning and return value unchanged
        raise NotImplementedError


# Sentinel returned by _apply_field when on_missing=="omit" — the project()
# caller checks for this and skips the key entirely.
_OMIT_SENTINEL = object()
