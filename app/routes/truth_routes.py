from fastapi import APIRouter, Request, Depends
from fastapi.responses import PlainTextResponse
import random
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..config import settings

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/truth", response_class=PlainTextResponse)
@limiter.limit(f"{settings.rate_limit.max_requests}/hour")
async def get_random_truth(request: Request):
    """Return a random truth from the collection"""
    try:
        truths = request.app.state.truths
        if not truths:
            return PlainTextResponse(
                content="Truth not found",
                status_code=500
            )
        
        selected_truth = random.choice(truths)
        return selected_truth["truth"]
    
    except KeyError:
        return PlainTextResponse(
            content="Truth not found",
            status_code=500
        )
    except Exception:
        return PlainTextResponse(
            content="Truth not found",
            status_code=500
        )
