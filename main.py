"""
Truth or Dare API
FastAPI backend for serving truth/dare prompts from JSON data files.
"""

import json
import logging
import random
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# ======================
# Configuration
# ======================

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

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
    dare = "dare"


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
            
            # Ensure both 'truth' and 'dare' keys exist
            if "truth" not in data:
                data["truth"] = []
            if "dare" not in data:
                data["dare"] = []
            
            cache[category] = data
            logger.info(f"Loaded category: {category} ({len(data['truth'])} truths, {len(data['dare'])} dares)")
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse {json_file}: {e}")
        except Exception as e:
            logger.error(f"Error loading {json_file}: {e}")
    
    if not cache:
        logger.warning("No data files loaded!")
    
    return cache


def reload_data() -> None:
    """Reload data from files into cache."""
    global DATA_CACHE
    DATA_CACHE = load_data_files()
    logger.info(f"Data reloaded. Categories: {list(DATA_CACHE.keys())}")


# ======================
# FastAPI App
# ======================

app = FastAPI(
    title="Truth or Dare API",
    description="API for serving random truth or dare prompts",
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
    """Load data into memory on application startup."""
    logger.info("Starting Truth or Dare API...")
    reload_data()
    
    if not DATA_CACHE:
        logger.warning("No data loaded. Application will return 404 for all requests.")
    else:
        logger.info(f"Application started with {len(DATA_CACHE)} categories")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Truth or Dare API...")


# ======================
# Endpoints
# ======================

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
    
    Returns count of truths and dares per category.
    """
    stats = {}
    for category, data in DATA_CACHE.items():
        stats[category] = {
            "truth_count": len(data.get("truth", [])),
            "dare_count": len(data.get("dare", [])),
            "total_count": len(data.get("truth", [])) + len(data.get("dare", []))
        }
    return stats


@app.get("/random", response_model=PromptResponse, tags=["Prompts"])
def get_random(
    type: Optional[PromptType] = Query(
        None,
        description="Filter by prompt type: 'truth' or 'dare'"
    ),
    category: str = Query(
        "default",
        description="Category name (e.g., 'default', 'spicy', 'family')"
    )
):
    """
    Get a random truth or dare prompt.
    
    Args:
        type: Optional filter for 'truth' or 'dare'
        category: Category name (default: 'default')
        
    Returns:
        Random prompt with type, text, and category
        
    Raises:
        HTTPException: 400 for invalid category, 404 for no data
    """
    # Validate and sanitize category
    try:
        category_path = safe_category_path(category)
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
    
    # Get prompts based on type filter
    if type:
        prompts = data.get(type.value, [])
        prompt_type = type.value
    else:
        # Combine both types and pick randomly
        all_prompts = []
        all_prompts.extend([("truth", t) for t in data.get("truth", [])])
        all_prompts.extend([("dare", d) for d in data.get("dare", [])])
        
        if not all_prompts:
            logger.warning(f"No prompts available in category: {category}")
            raise HTTPException(
                status_code=404,
                detail=f"No prompts available in category '{category}'"
            )
        
        prompt_type, prompt_text = random.choice(all_prompts)
        return {
            "type": prompt_type,
            "text": prompt_text,
            "category": category
        }
    
    # Return random prompt of specified type
    if not prompts:
        logger.warning(f"No {type.value}s available in category: {category}")
        raise HTTPException(
            status_code=404,
            detail=f"No {type.value}s available in category '{category}'"
        )
    
    return {
        "type": prompt_type,
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
