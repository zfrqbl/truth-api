from fastapi import FastAPI, HTTPException, Request
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
        <html>
        <head>
            <title>{settings.app.title}</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    margin: 0;
                    padding: 0;
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }}
                .container {{
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    padding: 40px;
                    max-width: 800px;
                    width: 90%;
                    text-align: center;
                    position: relative;
                    overflow: hidden;
                }}
                .container::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 5px;
                    background: linear-gradient(90deg, #667eea, #764ba2);
                }}
                h1 {{
                    color: #2c3e50;
                    margin: 0 0 20px 0;
                    font-size: 32px;
                }}
                p {{
                    color: #7f8c8d;
                    font-size: 18px;
                    line-height: 1.6;
                    margin: 0 0 30px 0;
                }}
                .section {{
                    background: #f8f9fa;
                    border-radius: 10px;
                    padding: 25px;
                    margin: 20px 0;
                    text-align: left;
                    border: 1px solid #e9ecef;
                }}
                .section-title {{
                    color: #2c3e50;
                    margin: 0 0 15px 0;
                    font-size: 20px;
                    font-weight: 600;
                }}
                .endpoint {{
                    background: white;
                    padding: 12px 15px;
                    margin: 10px 0;
                    border-radius: 6px;
                    border-left: 4px solid #667eea;
                    font-family: monospace;
                    font-size: 16px;
                    color: #2c3e50;
                }}
                .rate-limit {{
                    color: #e74c3c;
                    font-size: 14px;
                    margin-top: 5px;
                    display: block;
                }}
                .example {{
                    background: #2c3e50;
                    color: white;
                    padding: 12px 15px;
                    border-radius: 6px;
                    font-family: monospace;
                    font-size: 14px;
                    margin: 15px 0;
                    overflow-x: auto;
                }}
                .btn {{
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    padding: 12px 24px;
                    border-radius: 25px;
                    margin: 10px 5px;
                    font-size: 16px;
                    font-weight: 600;
                    transition: all 0.3s ease;
                    border: none;
                    cursor: pointer;
                }}
                .btn:hover {{
                    background: #5a6fd8;
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
                }}
                .btn-secondary {{
                    background: #6c757d;
                }}
                .btn-secondary:hover {{
                    background: #5a6268;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{settings.app.title}</h1>
                <p>{settings.app.description}</p>
                
                <div class="section">
                    <div class="section-title">Endpoints:</div>
                    <div class="endpoint">
                        GET {settings.api.endpoints.root}
                        <div class="rate-limit">Returns this documentation page</div>
                    </div>
                    <div class="endpoint">
                        GET {settings.api.endpoints.truth}
                        <div class="rate-limit">Returns a random truth with shareable link • Rate Limit: {settings.rate_limit.max_requests} requests per hour</div>
                    </div>
                    <div class="endpoint">
                        GET {settings.api.endpoints.health}
                        <div class="rate-limit">Returns health status of the API</div>
                    </div>
                    <div class="endpoint">
                        GET {settings.api.endpoints.truth}/{{truth_id}}
                        <div class="rate-limit">Returns a specific truth by ID with shareable link</div>
                    </div>
                </div>
                
                <div class="section">
                    <div class="section-title">Rate Limiting:</div>
                    <p>This API enforces a rate limit of {settings.rate_limit.max_requests} requests per hour per IP address.</p>
                </div>
                
                <div class="section">
                    <div class="section-title">Examples:</div>
                    <div class="example">curl -X GET https://your-railway-app.railway.app{settings.api.endpoints.truth}</div>
                    <div class="example">curl -X GET https://your-railway-app.railway.app{settings.api.endpoints.health}</div>
                </div>
                
                <div>
                    <a href="{settings.api.endpoints.truth}" class="btn">Get Random Truth</a>
                    <a href="{settings.api.endpoints.health}" class="btn btn-secondary">Check Health</a>
                </div>
            </div>
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
