#!/usr/bin/env python3
"""Main entry point for the UnspokenTruth API."""

import logging
import uvicorn
from config.loader import load_settings
from domain.store import load_truths
from api.api import TruthAPI
from api.app import create_app

# Boot sequence at module level for ASGI app loading
settings = load_settings()
truths = load_truths(settings)
api_instance = TruthAPI(settings, truths)
app = create_app(settings, api_instance)

# Configure logging after settings load
logging.basicConfig(
    level=getattr(logging, settings.observability.logging["level"]),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
