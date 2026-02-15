from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
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
    # Increment hit counter for each truth request
    request.app.state.hit_counter += 1
    
    try:
        truths = request.app.state.truths
        if not truths:
            return HTMLResponse(
                content="""
                <html>
                <head>
                    <title>Truth API</title>
                    <style>
                        body { 
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            margin: 0;
                            padding: 0;
                            min-height: 100vh;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                        }
                        .container {
                            background: white;
                            border-radius: 15px;
                            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                            padding: 40px;
                            max-width: 600px;
                            width: 90%;
                            text-align: center;
                        }
                        .error {
                            color: #e74c3c;
                            font-size: 18px;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1 class="error">Truth not found</h1>
                    </div>
                </body>
                </html>
                """,
                status_code=500
            )
        
        selected_truth = random.choice(truths)
        truth_text = selected_truth["truth"]
        truth_id = selected_truth["id"]
        
        # Construct the shareable link
        base_url = str(request.url).replace(str(request.url.path), "")
        shareable_link = f"{base_url}/truth/{truth_id}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Truth API</title>
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
                    max-width: 600px;
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
                .truth {{
                    font-size: 24px;
                    line-height: 1.6;
                    color: #2c3e50;
                    margin: 0 0 30px 0;
                    font-weight: 500;
                    position: relative;
                    padding: 0 20px;
                }}
                .share-section {{
                    background: #f8f9fa;
                    border-radius: 10px;
                    padding: 20px;
                    margin-top: 20px;
                    border: 1px solid #e9ecef;
                }}
                .share-label {{
                    display: block;
                    font-size: 14px;
                    color: #6c757d;
                    margin-bottom: 8px;
                    font-weight: 600;
                }}
                .share-link {{
                    font-size: 14px;
                    color: #667eea;
                    word-break: break-all;
                    text-decoration: none;
                    display: block;
                    padding: 8px 12px;
                    background: white;
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                    transition: all 0.3s ease;
                }}
                .share-link:hover {{
                    background: #667eea;
                    color: white;
                    border-color: #667eea;
                }}
                .refresh-btn {{
                    background: #667eea;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 25px;
                    cursor: pointer;
                    font-size: 16px;
                    margin-top: 20px;
                    transition: all 0.3s ease;
                    font-weight: 600;
                }}
                .refresh-btn:hover {{
                    background: #5a6fd8;
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
                }}
                .id-tag {{
                    position: absolute;
                    top: 15px;
                    right: 15px;
                    background: #e9ecef;
                    color: #6c757d;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 600;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="id-tag">{truth_id}</div>
                <p class="truth">"{truth_text}"</p>
                <div class="share-section">
                    <span class="share-label">Share this truth:</span>
                    <a href="{shareable_link}" class="share-link" target="_blank">{shareable_link}</a>
                </div>
                <button class="refresh-btn" onclick="location.reload()">Get Another Truth</button>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    
    except KeyError:
        return HTMLResponse(
            content="""
            <html>
            <head>
                <title>Truth API</title>
                <style>
                    body { 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        margin: 0;
                        padding: 0;
                        min-height: 100vh;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                    }
                    .container {
                        background: white;
                        border-radius: 15px;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                        padding: 40px;
                        max-width: 600px;
                        width: 90%;
                        text-align: center;
                    }
                    .error {
                        color: #e74c3c;
                        font-size: 18px;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1 class="error">Truth not found</h1>
                </div>
            </body>
            </html>
            """,
            status_code=500
        )
    except Exception:
        return HTMLResponse(
            content="""
            <html>
            <head>
                <title>Truth API</title>
                <style>
                    body { 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        margin: 0;
                        padding: 0;
                        min-height: 100vh;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                    }
                    .container {
                        background: white;
                        border-radius: 15px;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                        padding: 40px;
                        max-width: 600px;
                        width: 90%;
                        text-align: center;
                    }
                    .error {
                        color: #e74c3c;
                        font-size: 18px;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1 class="error">Truth not found</h1>
                </div>
            </body>
            </html>
            """,
            status_code=500
        )


@router.get("/truth/{truth_id}", response_class=HTMLResponse)
@limiter.limit(f"{settings.rate_limit.max_requests}/hour")
async def get_truth_by_id(request: Request, truth_id: str):
    """Return a specific truth by ID with a shareable link"""
    # Increment hit counter for each truth request
    request.app.state.hit_counter += 1
    
    try:
        truths = request.app.state.truths
        if not truths:
            return HTMLResponse(
                content="""
                <html>
                <head>
                    <title>Truth API</title>
                    <style>
                        body { 
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            margin: 0;
                            padding: 0;
                            min-height: 100vh;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                        }
                        .container {
                            background: white;
                            border-radius: 15px;
                            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                            padding: 40px;
                            max-width: 600px;
                            width: 90%;
                            text-align: center;
                        }
                        .error {
                            color: #e74c3c;
                            font-size: 18px;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1 class="error">Truth not found</h1>
                    </div>
                </body>
                </html>
                """,
                status_code=500
            )
        
        # Find the truth with the specified ID
        selected_truth = next((t for t in truths if t["id"] == truth_id), None)
        
        if not selected_truth:
            return HTMLResponse(
                content="""
                <html>
                <head>
                    <title>Truth API</title>
                    <style>
                        body { 
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            margin: 0;
                            padding: 0;
                            min-height: 100vh;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                        }
                        .container {
                            background: white;
                            border-radius: 15px;
                            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                            padding: 40px;
                            max-width: 600px;
                            width: 90%;
                            text-align: center;
                        }
                        .error {
                            color: #e74c3c;
                            font-size: 18px;
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1 class="error">Truth not found</h1>
                    </div>
                </body>
                </html>
                """,
                status_code=404
            )
        
        truth_text = selected_truth["truth"]
        
        # Construct the shareable link
        base_url = str(request.url).replace(str(request.url.path), "")
        shareable_link = f"{base_url}/truth/{truth_id}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Truth API</title>
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
                    max-width: 600px;
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
                .truth {{
                    font-size: 24px;
                    line-height: 1.6;
                    color: #2c3e50;
                    margin: 0 0 30px 0;
                    font-weight: 500;
                    position: relative;
                    padding: 0 20px;
                }}
                .share-section {{
                    background: #f8f9fa;
                    border-radius: 10px;
                    padding: 20px;
                    margin-top: 20px;
                    border: 1px solid #e9ecef;
                }}
                .share-label {{
                    display: block;
                    font-size: 14px;
                    color: #6c757d;
                    margin-bottom: 8px;
                    font-weight: 600;
                }}
                .share-link {{
                    font-size: 14px;
                    color: #667eea;
                    word-break: break-all;
                    text-decoration: none;
                    display: block;
                    padding: 8px 12px;
                    background: white;
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                    transition: all 0.3s ease;
                }}
                .share-link:hover {{
                    background: #667eea;
                    color: white;
                    border-color: #667eea;
                }}
                .refresh-btn {{
                    background: #667eea;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 25px;
                    cursor: pointer;
                    font-size: 16px;
                    margin-top: 20px;
                    transition: all 0.3s ease;
                    font-weight: 600;
                }}
                .refresh-btn:hover {{
                    background: #5a6fd8;
                    transform: translateY(-2px);
                    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
                }}
                .id-tag {{
                    position: absolute;
                    top: 15px;
                    right: 15px;
                    background: #e9ecef;
                    color: #6c757d;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 600;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="id-tag">{truth_id}</div>
                <p class="truth">"{truth_text}"</p>
                <div class="share-section">
                    <span class="share-label">Share this truth:</span>
                    <a href="{shareable_link}" class="share-link" target="_blank">{shareable_link}</a>
                </div>
                <button class="refresh-btn" onclick="location.href='/truth'">Get Another Truth</button>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    
    except KeyError:
        return HTMLResponse(
            content="""
            <html>
            <head>
                <title>Truth API</title>
                <style>
                    body { 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        margin: 0;
                        padding: 0;
                        min-height: 100vh;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                    }
                    .container {
                        background: white;
                        border-radius: 15px;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                        padding: 40px;
                        max-width: 600px;
                        width: 90%;
                        text-align: center;
                    }
                    .error {
                        color: #e74c3c;
                        font-size: 18px;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1 class="error">Truth not found</h1>
                </div>
            </body>
            </html>
            """,
            status_code=500
        )
    except Exception:
        return HTMLResponse(
            content="""
            <html>
            <head>
                <title>Truth API</title>
                <style>
                    body { 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        margin: 0;
                        padding: 0;
                        min-height: 100vh;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                    }
                    .container {
                        background: white;
                        border-radius: 15px;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                        padding: 40px;
                        max-width: 600px;
                        width: 90%;
                        text-align: center;
                    }
                    .error {
                        color: #e74c3c;
                        font-size: 18px;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1 class="error">Truth not found</h1>
                </div>
            </body>
            </html>
            """,
            status_code=500
        )
