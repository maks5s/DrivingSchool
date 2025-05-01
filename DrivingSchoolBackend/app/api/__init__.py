from fastapi import APIRouter

from core.config import settings
from .auth import router as auth_router
from .category_level import router as category_level_router
from .vehicle import router as vehicle_router
from .cabinet import router as cabinet_router
from .instructor import router as instructor_router

router = APIRouter(prefix=settings.api.prefix)
router.include_router(auth_router)
router.include_router(category_level_router)
router.include_router(vehicle_router)
router.include_router(cabinet_router)
router.include_router(instructor_router)
