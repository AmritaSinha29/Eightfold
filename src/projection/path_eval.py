"""Path expression evaluator for runtime config field remapping.

Supported syntax (an intentional subset — NOT full JSONPath):
  - "field"              → data["field"]                     (scalar)
  - "field[N]"           → data["field"][N]                  (Nth list element)
  - "field[].subfield"   → [item["subfield"] for item in data["field"]]  (map over list)

Any other syntax raises ValueError. This is documented in the README.
"""
from __future__ import annotations

import re
from typing import Any, Optional


# Pre-compiled patterns for the three supported path forms.
_SIMPLE = re.compile(r"^(\w+)$")
_INDEXED = re.compile(r"^(\w+)\[(\d+)\]$")
_MAP = re.compile(r"^(\w+)\[\]\.(\w+)$")


def evaluate_path(data: dict[str, Any], path: str) -> Any:
    """Evaluate a path expression against a profile dict.

    Args:
        data: Dict form of the CanonicalProfile (from CanonicalProfile.to_dict()).
        path: Path expression string (see module docstring for supported forms).

    Returns:
        The resolved value. Returns None if the path resolves to a missing
        key, an out-of-bounds index, or a None intermediate node.

    Raises:
        ValueError: If path does not match any supported syntax.

    Examples:
        >>> evaluate_path({"full_name": "Alice"}, "full_name")
        'Alice'
        >>> evaluate_path({"emails": ["a@b.com"]}, "emails[0]")
        'a@b.com'
        >>> evaluate_path({"skills": [{"name": "Python"}]}, "skills[].name")
        ['Python']
        >>> evaluate_path({"emails": []}, "emails[99]")
        None
    """
    # TODO: if m := _SIMPLE.match(path): return data.get(m.group(1))
    # TODO: if m := _INDEXED.match(path):
    #           lst = data.get(m.group(1), [])
    #           idx = int(m.group(2))
    #           return lst[idx] if idx < len(lst) else None
    # TODO: if m := _MAP.match(path):
    #           lst = data.get(m.group(1), [])
    #           return [item.get(m.group(2)) for item in lst if isinstance(item, dict)]
    # TODO: raise ValueError(f"Unsupported path expression: {path!r}. "
    #                        "Supported forms: 'field', 'field[N]', 'field[].subfield'")
    raise NotImplementedError
