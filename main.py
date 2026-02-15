import uvicorn
from app.main import app
from app.config import settings


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=int(settings.app.port),
        reload=False  # Disable reload in production
    )
