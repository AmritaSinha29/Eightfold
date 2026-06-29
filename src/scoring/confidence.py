"""Confidence scoring for fields and the overall canonical profile.

Confidence is a float in [0.0, 1.0]. The scoring model is:
  - Base confidence = max(SOURCE_BASE_CONFIDENCE[source] for source in contributing_sources)
  - Corroboration bonus = CORROBORATION_BONUS * (num_sources - 1)
  - Conflict penalty = CONFLICT_PENALTY if sources disagreed on the value
  - Final = clamp(base + bonus - penalty, 0.0, 1.0)

Overall profile confidence = weighted average of per-field scores,
with higher weights assigned to identity fields (name, email, phone).
"""
from __future__ import annotations

from src.models.canonical import CanonicalProfile


# Base confidence per source type, reflecting structure and reliability.
SOURCE_BASE_CONFIDENCE: dict[str, float] = {
    "csv": 0.90,
    "ats_json": 0.85,
    "linkedin": 0.75,
    "github": 0.70,
    "resume": 0.60,
    "notes": 0.40,
}

# Multiplier added per additional corroborating source.
CORROBORATION_BONUS: float = 0.05

# Subtracted when sources conflict on the field's value.
CONFLICT_PENALTY: float = 0.10

# Weights for overall_confidence computation (fields not listed get weight 1.0).
FIELD_WEIGHTS: dict[str, float] = {
    "full_name": 3.0,
    "emails": 2.5,
    "phones": 2.0,
    "location": 1.5,
    "skills": 1.5,
    "experience": 1.5,
    "education": 1.2,
    "headline": 1.0,
    "years_experience": 1.0,
    "links": 0.8,
}


def score_field(source_names: list[str], has_conflict: bool) -> float:
    """Compute confidence for a single field.

    Args:
        source_names: Names of sources that contributed to this field's value.
                      Must be non-empty.
        has_conflict: True if sources disagreed on this field's value.

    Returns:
        Confidence score clamped to [0.0, 1.0].
    """
    # TODO: base = max(SOURCE_BASE_CONFIDENCE.get(s, 0.3) for s in source_names)
    # TODO: bonus = CORROBORATION_BONUS * (len(source_names) - 1)
    # TODO: penalty = CONFLICT_PENALTY if has_conflict else 0.0
    # TODO: return max(0.0, min(1.0, base + bonus - penalty))
    raise NotImplementedError


def score_skill(corroborating_sources: int, total_sources: int) -> float:
    """Compute confidence for a single CanonicalSkill entry.

    A skill mentioned by more sources gets higher confidence.

    Args:
        corroborating_sources: Number of sources that mentioned this skill.
        total_sources: Total number of sources in the merge group.

    Returns:
        Confidence score in [0.0, 1.0].
    """
    # TODO: if total_sources == 0: return 0.0
    # TODO: ratio = corroborating_sources / total_sources
    # TODO: return max(0.0, min(1.0, ratio * 0.8 + 0.2))  # floor of 0.2 for any mention
    raise NotImplementedError


def score_profile(profile: CanonicalProfile) -> float:
    """Compute overall_confidence as a weighted average of per-field scores.

    Fields present in the profile are re-scored from their provenance entries.
    Fields that are None contribute 0 (no confidence) at their weight.

    Args:
        profile: The fully merged canonical profile.

    Returns:
        Overall confidence score in [0.0, 1.0].
    """
    # TODO: For each field in FIELD_WEIGHTS:
    #   - Find provenance entries for this field
    #   - If none: contribution = 0
    #   - Else: score_field([prov.source for prov in entries], has_conflict=len(entries) > 1)
    # TODO: weighted_sum / total_weight → round to 4 decimal places
    raise NotImplementedError
