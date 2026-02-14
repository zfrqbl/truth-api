import time
import json
import logging
import uuid
from collections import defaultdict
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from config.models import Settings

# In-memory store for rate limiting
rate_limit_store: dict[str, list[float]] = defaultdict(list)

logger = logging.getLogger(__name__)


def rate_limit_middleware(settings: Settings):
    """Middleware for rate limiting and logging."""
    async def middleware(request: Request, call_next):
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.time()

        # Check if exempt from rate limiting
        if request.url.path in settings.rate_limit.exempt_routes:
            response = await call_next(request)
            add_headers(response, settings)
            await log_request(request, response, settings, start_time)
            return response

        # Rate limiting logic
        key = get_rate_limit_key(request, settings)
        now = time.time()
        timestamps = rate_limit_store[key]
        period = settings.rate_limit.period_seconds
        limit = settings.rate_limit.requests_per_period

        # Remove expired timestamps
        timestamps[:] = [t for t in timestamps if now - t < period]

        if len(timestamps) >= limit:
            # Rate limited
            oldest = min(timestamps)
            retry_after = int(period - (now - oldest))
            error_data = {
                settings.errors.field_names["error"]: "rate_limited",
                settings.errors.field_names["message"]: "Rate limit exceeded",
                settings.errors.field_names["request_id"]: request_id,
                settings.errors.field_names["retry_after_seconds"]: retry_after
            }
            response = JSONResponse(
                status_code=settings.errors.status_mappings["rate_limited"],
                content=error_data
            )
            add_headers(response, settings)
            await log_request(request, response, settings, start_time)
            return response

        # Add current timestamp
        timestamps.append(now)

        response = await call_next(request)
        add_headers(response, settings)
        await log_request(request, response, settings, start_time)
        return response

    return middleware


def get_rate_limit_key(request: Request, settings: Settings) -> str:
    """Get the key for rate limiting based on strategy."""
    if settings.rate_limit.key_strategy == "remote_address":
        return request.client.host or "unknown"
    return "default"


def add_headers(response: Response, settings: Settings):
    """Add required headers to the response."""
    response.headers["Cache-Control"] = settings.headers.cache_control
    response.headers["Vary"] = settings.headers.vary
    for key, value in settings.headers.security.items():
        header_key = key.replace("_", "-")
        response.headers[header_key] = value


async def log_request(request: Request, response: Response, settings: Settings, start_time: float):
    """Log the request details."""
    end_time = time.time()
    latency = end_time - start_time
    log_data = {
        "request_id": request.state.request_id,
        "endpoint": request.url.path,
        "status": response.status_code,
        "latency": latency,
        "truth_id": getattr(request.state, "truth_id", None),
        "day": getattr(request.state, "day", None)
    }
    log_format = settings.observability.logging.get("format", "text")
    if log_format == "json":
        logger.info(json.dumps(log_data))
    else:
        logger.info(f"Request: {log_data}")
