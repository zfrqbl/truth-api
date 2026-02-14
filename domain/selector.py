import random
from datetime import datetime, timezone
from typing import List
from .models import Truth
from config.models import Settings


def get_current_day() -> str:
    """Get current UTC weekday as string (e.g., 'Monday')."""
    return datetime.now(timezone.utc).strftime('%A')


def select_truth(truths: List[Truth], settings: Settings) -> Truth:
    """Select a truth based on current day and weight probabilities."""
    day = get_current_day()
    day_weights = settings.selection.day_weight_table[day]
    weights = [day_weights[t.weight] for t in truths]
    selected = random.choices(truths, weights=weights, k=1)[0]
    return selected
