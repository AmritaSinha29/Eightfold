"""Projection layer — reshapes a candidate dict into the requested output shape."""
from __future__ import annotations

import logging
from typing import Any, Optional

from src.projection.config_parser import FieldSpec, OutputConfig
from src.projection.path_eval import evaluate_path
from src.projection.validator import validate_output

logger = logging.getLogger(__name__)

# Sentinel — returned by _apply_field when the key should be omitted entirely.
_OMIT = object()


class Projector:
    """Applies an OutputConfig to a plain candidate dict and returns a serializable dict."""

    def project(self, data: dict[str, Any], config: OutputConfig) -> dict[str, Any]:
        """Reshape a candidate dict into a final output dict per config."""
        result: dict[str, Any] = {}

        for spec in config.fields:
            key, val = self._apply_field(data, spec, config)
            if val is _OMIT:
                continue
            result[key] = val

        if config.include_confidence and "overall_confidence" not in result:
            result["overall_confidence"] = data.get("overall_confidence")
        if config.include_provenance and "provenance" not in result:
            result["provenance"] = data.get("provenance", [])

        validate_output(result, config)
        return result

    def _apply_field(
        self,
        data: dict[str, Any],
        spec: FieldSpec,
        config: OutputConfig,
    ) -> tuple[str, Any]:
        path = spec.from_path if spec.from_path else spec.path
        value = evaluate_path(data, path)

        if value is None:
            if config.on_missing == "error" and spec.required:
                raise ValueError(f"Required field '{spec.path}' is missing from profile")
            if config.on_missing == "omit":
                return (spec.path, _OMIT)
            # on_missing == "null" — fall through with value = None

        value = self._apply_normalize(value, spec.normalize)
        return (spec.path, value)

    def _apply_normalize(self, value: Any, normalize: Optional[str]) -> Any:
        if normalize is None:
            return value
        if normalize == "E164":
            from src.normalizers.phone import normalize_phone, normalize_phones
            if isinstance(value, list):
                return normalize_phones(value)
            return normalize_phone(str(value)) if value is not None else value
        if normalize == "canonical":
            from src.normalizers.skills import canonicalize_skill, canonicalize_skills
            if isinstance(value, list):
                return canonicalize_skills([str(v) for v in value])
            return canonicalize_skill(str(value)) if value is not None else value
        logger.warning("Unknown normalize token %r — value returned unchanged", normalize)
        return value
