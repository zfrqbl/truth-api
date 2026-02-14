#!/usr/bin/env python3
"""Main entry point for the UnspokenTruth API."""

import logging
import uvicorn
from config.loader import load_settings
from domain.store import load_truths
from api.api import TruthAPI
from api.app import create_app


def main():
    """Boot sequence for the API."""
    # 1. Load config
    print("Loading configuration...")
    settings = load_settings()
    print("Configuration loaded and validated.")

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.observability.logging["level"]),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 2. Load truths file
    print("Loading truths...")
    truths = load_truths(settings)
    print(f"Truths loaded and validated: {len(truths)} truths.")

    # 3. Build selector (functions are ready)
    # 4. Build middleware (in create_app)
    # 5. Register routes (in create_app)

    # Create API instance
    api_instance = TruthAPI(settings, truths)

    # Create FastAPI app
    app = create_app(settings, api_instance)
    print("Application built successfully.")

    # 6. Start server
    print("Starting server...")
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
