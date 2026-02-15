from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse
from contextlib import asynccontextmanager
import json
import random
from datetime import datetime
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .config import settings
from .routes.truth_routes import router as truth_router


# Initialize limiter globally
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.truths = load_truths()
    yield
    # Shutdown


def load_truths():
    """Load truths from JSON file"""
    try:
        with open(settings.files.truth_file_path, 'r', encoding='utf-8') as file:
            truths = json.load(file)
        return truths
    except FileNotFoundError:
        raise Exception(f"Truth file not found at {settings.files.truth_file_path}")
    except json.JSONDecodeError:
        raise Exception(f"Invalid JSON in truth file at {settings.files.truth_file_path}")


def create_app():
    """Create and configure FastAPI application"""
    app = FastAPI(
        title=settings.app.title,
        description=settings.app.description,
        version=settings.app.version,
        lifespan=lifespan
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.allow_origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers,
    )

    # Add rate limit exception handler
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Include routers
    app.include_router(truth_router, prefix="")

    @app.get(settings.api.endpoints.root, response_class=HTMLResponse)
    async def root(request: Request):
        """Root endpoint with API documentation"""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{settings.app.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #333; }}
                .endpoint {{ background-color: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 4px; }}
                .rate-limit {{ color: #d9534f; }}
            </style>
        </head>
        <body>
            <h1>{settings.app.title}</h1>
            <p>{settings.app.description}</p>
            
            <h2>Endpoints:</h2>
            <div class="endpoint">
                <strong>GET {settings.api.endpoints.root}</strong><br>
                Returns this documentation page
            </div>
            <div class="endpoint">
                <strong>GET {settings.api.endpoints.truth}</strong><br>
                Returns a random truth from the collection<br>
                <span class="rate-limit">Rate Limit: {settings.rate_limit.max_requests} requests per hour</span>
            </div>
            
            <h2>Rate Limiting:</h2>
            <p>This API enforces a rate limit of {settings.rate_limit.max_requests} requests per hour per IP address.</p>
            
            <h2>Examples:</h2>
            <pre>curl -X GET https://truth-api-production.up.railway.app{settings.api.endpoints.truth}</pre>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    @app.get(settings.api.endpoints.health)
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "version": settings.app.version,
            "timestamp": datetime.utcnow().isoformat()
        }

    return app


app = create_app()
