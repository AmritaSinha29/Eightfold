"""Output schema validation using jsonschema.

Converts an OutputConfig into a JSON Schema dict and validates the projected
output against it. Validation errors are raised as ValueError with a clear
message identifying which field failed and why.
"""
from __future__ import annotations

from typing import Any

from src.projection.config_parser import FieldSpec, OutputConfig


# Maps config type strings to JSON Schema type strings.
TYPE_MAP: dict[str, Any] = {
    "string": "string",
    "string[]": {"type": "array", "items": {"type": "string"}},
    "number": "number",
    "boolean": "boolean",
    "object": "object",
    "object[]": {"type": "array", "items": {"type": "object"}},
}


def validate_output(output: dict[str, Any], config: OutputConfig) -> None:
    """Validate the projected output dict against the config-declared schema.

    Args:
        output: The projected output dict to validate.
        config: The output config that declared the expected fields and types.

    Raises:
        ValueError: If a required field is missing or a value has the wrong type.
                    The message names the offending field and describes the violation.
    """
    # TODO: schema = build_json_schema(config)
    # TODO: import jsonschema
    # TODO: try: jsonschema.validate(output, schema)
    # TODO: except jsonschema.ValidationError as e: raise ValueError(f"Output validation failed: {e.message}") from e
    raise NotImplementedError


def build_json_schema(config: OutputConfig) -> dict[str, Any]:
    """Convert an OutputConfig into a JSON Schema dict for use with jsonschema.validate().

    Args:
        config: The output config to convert.

    Returns:
        A JSON Schema dict: {"type": "object", "properties": {...}, "required": [...]}.
    """
    # TODO: properties = {}
    # TODO: required = []
    # TODO: For each spec in config.fields:
    #           properties[spec.path] = TYPE_MAP.get(spec.type, {}) if spec.type else {}
    #           if spec.required: required.append(spec.path)
    # TODO: return {"type": "object", "properties": properties, "required": required}
    raise NotImplementedError
