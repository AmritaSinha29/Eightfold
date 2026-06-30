"""Confidence scoring for fields and the overall canonical profile."""
from __future__ import annotations

from collections import defaultdict

from src.models.canonical import CanonicalProfile


SOURCE_BASE_CONFIDENCE: dict[str, float] = {
    "csv":      0.90,
    "ats_json": 0.85,
    "linkedin": 0.75,
    "github":   0.70,
    "resume":   0.60,
    "notes":    0.40,
}

CORROBORATION_BONUS: float = 0.05
CONFLICT_PENALTY:    float = 0.10

FIELD_WEIGHTS: dict[str, float] = {
    "full_name":        3.0,
    "emails":           2.5,
    "phones":           2.0,
    "location":         1.5,
    "skills":           1.5,
    "experience":       1.5,
    "education":        1.2,
    "headline":         1.0,
    "years_experience": 1.0,
    "links":            0.8,
}


def score_field(source_names: list[str], has_conflict: bool) -> float:
    """Compute confidence for a single field from its contributing sources."""
    base    = max(SOURCE_BASE_CONFIDENCE.get(s, 0.3) for s in source_names)
    bonus   = CORROBORATION_BONUS * (len(source_names) - 1)
    penalty = CONFLICT_PENALTY if has_conflict else 0.0
    return max(0.0, min(1.0, base + bonus - penalty))


def score_skill(corroborating_sources: int, total_sources: int) -> float:
    """Compute confidence for one CanonicalSkill entry."""
    if total_sources == 0:
        return 0.0
    ratio = corroborating_sources / total_sources
    return max(0.0, min(1.0, ratio * 0.8 + 0.2))


def score_profile(profile: CanonicalProfile) -> float:
    """Compute overall_confidence as a weighted average of per-field scores."""
    prov_by_field: dict[str, list] = defaultdict(list)
    for entry in profile.provenance:
        # "location.city" → "location", "skills[0]" → "skills"
        base = entry.field.split(".")[0].split("[")[0]
        prov_by_field[base].append(entry)

    weighted_sum = 0.0
    total_weight = 0.0
    for field_name, weight in FIELD_WEIGHTS.items():
        entries = prov_by_field.get(field_name, [])
        if entries:
            sources = [e.source for e in entries]
            has_conflict = len(set(sources)) > 1
            field_score = score_field(sources, has_conflict)
        else:
            field_score = 0.0
        weighted_sum += weight * field_score
        total_weight += weight

    if total_weight == 0.0:
        return 0.0
    return round(weighted_sum / total_weight, 4)
