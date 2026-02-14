from domain.models import Truth
from domain.selector import select_truth, get_current_day
from config.models import Settings


class TruthAPI:
    """API logic for truth and health endpoints."""

    def __init__(self, settings: Settings, truths: list[Truth]):
        self.settings = settings
        self.truths = truths

    def get_truth_response(self) -> dict:
        """Generate the truth response data."""
        selected = select_truth(self.truths, self.settings)
        day = get_current_day()
        return {
            "truth": selected.truth,
            "category": selected.category,
            "day": day,
            "weight": selected.weight,
            "id": selected.id
        }

    def get_health_response(self) -> dict:
        """Generate the health response data."""
        return {"status": "healthy"}
