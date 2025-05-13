from fastapi import APIRouter

from core.config import settings
from .test_endpoints import router as test_router
from .auth import router as auth_router
from .user import router as user_router
from .category_level import router as category_level_router
from .vehicle import router as vehicle_router
from .cabinet import router as cabinet_router
from .instructor import router as instructor_router
from .group import router as group_router
from .student import router as student_router
from .group_schedule import router as group_schedule_router
from .practice_schedule import router as practice_schedule_router
from .admin import router as admin_router
from .statistics import router as statistics_router

router = APIRouter(prefix=settings.api.prefix)
router.include_router(test_router)
router.include_router(auth_router)
router.include_router(user_router)
router.include_router(category_level_router)
router.include_router(vehicle_router)
router.include_router(cabinet_router)
router.include_router(instructor_router)
router.include_router(group_router)
router.include_router(student_router)
router.include_router(group_schedule_router)
router.include_router(practice_schedule_router)
router.include_router(admin_router)
router.include_router(statistics_router)
