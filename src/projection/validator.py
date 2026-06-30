"""Output schema validation using jsonschema."""
from __future__ import annotations

from typing import Any

import jsonschema

from src.projection.config_parser import OutputConfig

TYPE_MAP: dict[str, Any] = {
    "string":   "string",
    "string[]": {"type": "array", "items": {"type": "string"}},
    "number":   "number",
    "boolean":  "boolean",
    "object":   "object",
    "object[]": {"type": "array", "items": {"type": "object"}},
}


def validate_output(output: dict[str, Any], config: OutputConfig) -> None:
    """Validate the projected output against the config-declared schema."""
    schema = build_json_schema(config)
    try:
        jsonschema.validate(output, schema)
    except jsonschema.ValidationError as exc:
        raise ValueError(f"Output validation failed: {exc.message}") from exc


def build_json_schema(config: OutputConfig) -> dict[str, Any]:
    """Convert an OutputConfig into a JSON Schema dict."""
    properties: dict[str, Any] = {}
    required: list[str] = []

    for spec in config.fields:
        if spec.type:
            type_info = TYPE_MAP.get(spec.type, {})
            if isinstance(type_info, str):
                # Allow null for optional fields so on_missing="null" passes validation
                schema_type: Any = {"type": type_info} if spec.required else {"type": [type_info, "null"]}
            else:
                schema_type = type_info
            properties[spec.path] = schema_type
        else:
            properties[spec.path] = {}

        if spec.required:
            required.append(spec.path)

    schema: dict[str, Any] = {"type": "object", "properties": properties}
    if required:
        schema["required"] = required
    return schema
