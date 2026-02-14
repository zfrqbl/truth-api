import yaml
from pathlib import Path
from .models import Settings


def load_settings() -> Settings:
    """Load and validate settings from YAML file."""
    settings_path = Path(__file__).parent.parent / "app" / "settings.yaml"
    with open(settings_path, 'r') as file:
        data = yaml.safe_load(file)
    return Settings(**data)
