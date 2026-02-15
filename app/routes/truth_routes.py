from fastapi import APIRouter, Request, Depends
from fastapi.responses import PlainTextResponse, HTMLResponse
import random
from slowapi import Limiter
from slowapi.util import get_remote_address
from urllib.parse import urljoin
from ..config import settings

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/truth", response_class=HTMLResponse)
@limiter.limit(f"{settings.rate_limit.max_requests}/hour")
async def get_random_truth(request: Request):
    """Return a random truth from the collection with a shareable link"""
    try:
        truths = request.app.state.truths
        if not truths:
            return HTMLResponse(
                content="<h1>Truth not found</h1>",
                status_code=500
            )
        
        selected_truth = random.choice(truths)
        truth_text = selected_truth["truth"]
        truth_id = selected_truth["id"]
        
        # Construct the shareable link
        base_url = str(request.url).replace(str(request.url.path), "")
        shareable_link = f"{base_url}/truth/{truth_id}"
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
            <p style="font-size: 18px; line-height: 1.6;">{truth_text}</p>
            <hr style="margin: 20px 0;">
            <div style="font-size: 14px; color: #666;">
                <p>Share this truth:</p>
                <a href="{shareable_link}" target="_blank">{shareable_link}</a>
            </div>
        </div>
        """
        return HTMLResponse(content=html_content)
    
    except KeyError:
        return HTMLResponse(
            content="<h1>Truth not found</h1>",
            status_code=500
        )
    except Exception:
        return HTMLResponse(
            content="<h1>Truth not found</h1>",
            status_code=500
        )


@router.get("/truth/{truth_id}", response_class=HTMLResponse)
@limiter.limit(f"{settings.rate_limit.max_requests}/hour")
async def get_truth_by_id(request: Request, truth_id: str):
    """Return a specific truth by ID with a shareable link"""
    try:
        truths = request.app.state.truths
        if not truths:
            return HTMLResponse(
                content="<h1>Truth not found</h1>",
                status_code=500
            )
        
        # Find the truth with the specified ID
        selected_truth = next((t for t in truths if t["id"] == truth_id), None)
        
        if not selected_truth:
            return HTMLResponse(
                content="<h1>Truth not found</h1>",
                status_code=404
            )
        
        truth_text = selected_truth["truth"]
        
        # Construct the shareable link
        base_url = str(request.url).replace(str(request.url.path), "")
        shareable_link = f"{base_url}/truth/{truth_id}"
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
            <p style="font-size: 18px; line-height: 1.6;">{truth_text}</p>
            <hr style="margin: 20px 0;">
            <div style="font-size: 14px; color: #666;">
                <p>Share this truth:</p>
                <a href="{shareable_link}" target="_blank">{shareable_link}</a>
            </div>
        </div>
        """
        return HTMLResponse(content=html_content)
    
    except KeyError:
        return HTMLResponse(
            content="<h1>Truth not found</h1>",
            status_code=500
        )
    except Exception:
        return HTMLResponse(
            content="<h1>Truth not found</h1>",
            status_code=500
        )
