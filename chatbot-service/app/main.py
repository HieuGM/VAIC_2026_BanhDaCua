from fastapi import FastAPI

from api.chat_routes import router as chat_router
from api.health_routes import router as health_router
from app.config import get_settings
from app.logger import setup_logging


setup_logging()
settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(health_router)
app.include_router(chat_router, prefix=settings.api_prefix)
