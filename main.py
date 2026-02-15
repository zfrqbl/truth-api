"""
Truth API
Simple, secure API for random truth prompts.
"""

import json
import logging
import random
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# ======================
# Configuration
# ======================

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("truth-api")

# ======================
# Data Models
# ======================

class PromptType(str, Enum):
    """Valid prompt types for filtering."""
    truth = "truth"


class PromptResponse(BaseModel):
    """Response model for a prompt."""
    type: str
    text: str
    category: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    data_loaded: bool


# ======================
# HTML Content Cache
# ======================

ROOT_HTML_CONTENT: Optional[str] = None


def load_root_html() -> str:
    """Load root HTML page content from static/index.html"""
    html_path = STATIC_DIR / "index.html"
    
    if not html_path.exists():
        logger.warning(f"Root HTML page not found at {html_path}. Using fallback content.")
        return """
        <!DOCTYPE html>
        <html>
        <head><title>Truth API</title></head>
        <body>
            <h1>Truth API</h1>
            <p>Simple API for random truth prompts</p>
            <p><a href="/docs">API Documentation</a></p>
            <p><a href="/health">Health Check</a></p>
            <p><a href="/random">Get Random Truth</a></p>
        </body>
        </html>
        """
    
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
        logger.info(f"Loaded root HTML page from {html_path}")
        return content
    except Exception as e:
        logger.error(f"Failed to load root HTML page: {e}")
        return f"<h1>Truth API</h1><p>Error loading page: {e}</p>"


# ======================
# Data Cache
# ======================

DATA_CACHE: Dict[str, Dict[str, List[str]]] = {}


def safe_category_path(category: str) -> Path:
    """
    Validate and sanitize category name to prevent path traversal attacks.
    
    Args:
        category: User-provided category name
        
    Returns:
        Path object for the category file
        
    Raises:
        ValueError: If category name is invalid
    """
    # Reject empty or None
    if not category or not isinstance(category, str):
        raise ValueError("Category must be a non-empty string")
    
    # Reject path traversal attempts
    if any(char in category for char in ["..", "/", "\\", "~"]):
        raise ValueError("Invalid category name")
    
    # Reject control characters
    if any(ord(c) < 32 for c in category):
        raise ValueError("Invalid category name")
    
    return DATA_DIR / f"{category}.json"


def load_data_files() -> Dict[str, Dict[str, List[str]]]:
    """
    Load all JSON data files from the data directory into memory.
    
    Returns:
        Dictionary mapping category names to their data
    """
    cache: Dict[str, Dict[str, List[str]]] = {}
    
    if not DATA_DIR.exists():
        logger.error(f"Data directory not found: {DATA_DIR}")
        return cache
    
    for json_file in DATA_DIR.glob("*.json"):
        category = json_file.stem
        
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Validate data structure
            if not isinstance(data, dict):
                logger.error(f"Invalid data structure in {json_file}")
                continue
            
            # Ensure 'truth' key exists (this is Truth API, not Truth or Dare)
            if "truth" not in data:
                data["truth"] = []
            
            cache[category] = data
            logger.info(f"Loaded category: {category} ({len(data['truth'])} truths)")
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse {json_file}: {e}")
        except Exception as e:
            logger.error(f"Error loading {json_file}: {e}")
    
    if not cache:
        logger.warning("No data files loaded!")
    
    return cache


def reload_data() -> None:
    """Reload data from files into cache."""
    global DATA_CACHE, ROOT_HTML_CONTENT
    DATA_CACHE = load_data_files()
    ROOT_HTML_CONTENT = load_root_html()
    logger.info(f"Data reloaded. Categories: {list(DATA_CACHE.keys())}")


# ======================
# FastAPI App
# ======================

app = FastAPI(
    title="Truth API",
    description="Simple, secure API for random truth prompts",
    version="1.0.0",
    contact={
        "name": "Zafar Iqbal",
        "email": "q.q@mybox.com",
    },
    license_info={
        "name": "MIT License",
    },
)


@app.on_event("startup")
async def startup_event():
    """Load data and HTML content into memory on application startup."""
    logger.info("Starting Truth API...")
    reload_data()
    
    if not DATA_CACHE:
        logger.warning("No data loaded. Application will return 404 for prompt requests.")
    else:
        logger.info(f"Application started with {len(DATA_CACHE)} categories")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Truth API...")


# ======================
# Endpoints
# ======================

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root():
    """
    Root endpoint - Beautiful HTML landing page.
    """
    global ROOT_HTML_CONTENT
    if ROOT_HTML_CONTENT is None:
        ROOT_HTML_CONTENT = load_root_html()
    return ROOT_HTML_CONTENT


@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """
    Health check endpoint.
    
    Returns status information about the API.
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "data_loaded": len(DATA_CACHE) > 0
    }


@app.get("/categories", response_model=List[str], tags=["Metadata"])
def get_categories():
    """
    Get list of available categories.
    
    Returns all category names that have data loaded.
    """
    return list(DATA_CACHE.keys())


@app.get("/stats", response_model=Dict[str, Dict[str, int]], tags=["Metadata"])
def get_stats():
    """
    Get statistics about loaded data.
    
    Returns count of truths per category.
    """
    stats = {}
    for category, data in DATA_CACHE.items():
        stats[category] = {
            "truth_count": len(data.get("truth", [])),
            "total_count": len(data.get("truth", []))
        }
    return stats


@app.get("/random", response_model=PromptResponse, tags=["Prompts"])
def get_random(
    category: str = Query(
        "default",
        description="Category name (e.g., 'default', 'spicy', 'family')"
    )
):
    """
    Get a random truth prompt.
    
    Args:
        category: Category name (default: 'default')
        
    Returns:
        Random truth prompt with type, text, and category
        
    Raises:
        HTTPException: 400 for invalid category, 404 for no data
    """
    # Validate and sanitize category
    try:
        safe_category_path(category)
    except ValueError as e:
        logger.warning(f"Invalid category request: {category} - {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category: {str(e)}"
        )
    
    # Check if category exists in cache
    if category not in DATA_CACHE:
        logger.warning(f"Category not found: {category}")
        raise HTTPException(
            status_code=404,
            detail=f"Category '{category}' not found. Available categories: {list(DATA_CACHE.keys())}"
        )
    
    data = DATA_CACHE[category]
    prompts = data.get("truth", [])
    
    # Return random prompt
    if not prompts:
        logger.warning(f"No truths available in category: {category}")
        raise HTTPException(
            status_code=404,
            detail=f"No truths available in category '{category}'"
        )
    
    return {
        "type": "truth",
        "text": random.choice(prompts),
        "category": category
    }


@app.get("/reload", tags=["Admin"])
def reload_endpoint():
    """
    Reload data from files (admin endpoint).
    
    WARNING: This endpoint should be protected in production!
    """
    reload_data()
    return {
        "message": "Data reloaded successfully",
        "categories": list(DATA_CACHE.keys())
    }


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler."""
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# ======================
# Development Server
# ======================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
