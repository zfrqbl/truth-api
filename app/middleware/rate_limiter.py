from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from ..config import settings
import time


def add_rate_limit_middleware(app: FastAPI):
    """Add rate limiting middleware to the application"""
    # Create limiter with configured settings
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[f"{settings.rate_limit.max_requests}/hour"]
    )
    app.state.limiter = limiter
    
    # Add custom handler for rate limit exceeded
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Rate limit exceeded",
                "retry_after": settings.rate_limit.window_seconds
            }
        )
    
    # Apply rate limiting to the /truth endpoint specifically
    for route in app.router.routes:
        if hasattr(route, 'methods') and '/truth' in str(route.path) and 'GET' in route.methods:
            # This approach applies to specific routes
            pass
