from fastapi import APIRouter
from .health import router as health_router
from .episodes import router as episodes_router
from .projects import router as projects_router
from .search import router as search_router
from .processing import router as processing_router
from .notifications import router as notifications_router
from .settings import router as settings_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(episodes_router)
api_router.include_router(projects_router)
api_router.include_router(search_router)
api_router.include_router(processing_router)
api_router.include_router(notifications_router)
api_router.include_router(settings_router)
