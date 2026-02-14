import json
from pathlib import Path
from typing import List
from .models import Truth
from config.models import Settings


def load_truths(settings: Settings) -> List[Truth]:
    """Load truths from JSON file and validate."""
    path = Path(settings.truths.source_file)
    with open(path, 'r') as file:
        data = json.load(file)
    truths = [Truth(**t) for t in data['truths']]
    validate_truths(truths, settings)
    return truths


def validate_truths(truths: List[Truth], settings: Settings):
    """Validate truths according to config rules."""
    ids = set()
    normalized_truths = set()
    allowed_weights = set(settings.truths.validation['allowed_weights'])
    min_count = settings.truths.validation['min_count']

    if len(truths) < min_count:
        raise ValueError(f"Truth count {len(truths)} below minimum {min_count}")

    for t in truths:
        if t.id in ids:
            raise ValueError(f"Duplicate id: {t.id}")
        ids.add(t.id)

        norm_truth = t.truth.lower().strip() if settings.truths.validation['normalize_truths'] else t.truth
        if norm_truth in normalized_truths:
            raise ValueError(f"Duplicate normalized truth: {t.truth}")
        normalized_truths.add(norm_truth)

        if t.weight not in allowed_weights:
            raise ValueError(f"Invalid weight '{t.weight}' for truth {t.id}. Allowed: {allowed_weights}")
