from fastapi import APIRouter

from core.config import settings
from .auth import router as auth_router
from .category_level import router as category_level_router

router = APIRouter(prefix=settings.api.prefix)
router.include_router(auth_router)
router.include_router(category_level_router)
