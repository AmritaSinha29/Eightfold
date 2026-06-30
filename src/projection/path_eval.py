"""Path expression evaluator for runtime config field remapping.

Supported forms:
  "field"            → data["field"]
  "field[N]"         → data["field"][N]
  "field[].subfield" → [item["subfield"] for item in data["field"]]
"""
from __future__ import annotations

import re
from typing import Any, Optional

_SIMPLE        = re.compile(r"^(\w+)$")
_INDEXED       = re.compile(r"^(\w+)\[(\d+)\]$")
_INDEXED_FIELD = re.compile(r"^(\w+)\[(\d+)\]\.(\w+)$")
_MAP           = re.compile(r"^(\w+)\[\]\.(\w+)$")


def evaluate_path(data: dict[str, Any], path: str) -> Any:
    """Evaluate a path expression against a profile dict.

    Supported forms:
      field              → scalar
      field[N]           → Nth list element
      field[N].subfield  → subfield of Nth list element
      field[].subfield   → subfield mapped over entire list

    Returns None for missing keys or out-of-bounds indices.
    Raises ValueError for unrecognised syntax.
    """
    if m := _SIMPLE.match(path):
        return data.get(m.group(1))

    if m := _INDEXED_FIELD.match(path):
        lst = data.get(m.group(1)) or []
        idx = int(m.group(2))
        item = lst[idx] if idx < len(lst) else None
        if not isinstance(item, dict):
            return None
        return item.get(m.group(3))

    if m := _INDEXED.match(path):
        lst = data.get(m.group(1)) or []
        idx = int(m.group(2))
        return lst[idx] if idx < len(lst) else None

    if m := _MAP.match(path):
        lst = data.get(m.group(1)) or []
        return [item.get(m.group(2)) for item in lst if isinstance(item, dict)]

    raise ValueError(
        f"Unsupported path expression: {path!r}. "
        "Supported forms: 'field', 'field[N]', 'field[N].subfield', 'field[].subfield'"
    )
