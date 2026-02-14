from fastapi import FastAPI, Header, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from .api import TruthAPI
from config.models import Settings
from core.middleware import rate_limit_middleware
from core.exceptions import APIError
import uuid


def create_app(settings: Settings, api_instance: TruthAPI) -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI()

    # Add middleware
    app.middleware("http")(rate_limit_middleware(settings))

    # Add exception handlers
    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError):
        error_data = {
            settings.errors.field_names["error"]: exc.error_type,
            settings.errors.field_names["message"]: exc.message,
            settings.errors.field_names["request_id"]: exc.request_id or getattr(request.state, "request_id", str(uuid.uuid4())),
            settings.errors.field_names["retry_after_seconds"]: exc.retry_after
        }
        return JSONResponse(status_code=exc.status_code, content=error_data)

    @app.exception_handler(Exception)
    async def general_error_handler(request: Request, exc: Exception):
        error_data = {
            settings.errors.field_names["error"]: "internal",
            settings.errors.field_names["message"]: "Internal server error",
            settings.errors.field_names["request_id"]: getattr(request.state, "request_id", str(uuid.uuid4())),
            settings.errors.field_names["retry_after_seconds"]: None
        }
        return JSONResponse(status_code=500, content=error_data)

    truth_endpoint = settings.api.endpoints["truth"]
    health_endpoint = settings.api.endpoints["health"]
    plain_accept = settings.api.content_negotiation["plain_text_accept"]

    @app.get(truth_endpoint)
    def get_truth(request: Request, accept: str = Header(None)):
        data = api_instance.get_truth_response()
        request.state.truth_id = data["id"]
        request.state.day = data["day"]
        if accept and plain_accept in accept:
            return PlainTextResponse(data["truth"])
        return data

    @app.get(health_endpoint)
    def get_health():
        return api_instance.get_health_response()

    return app
