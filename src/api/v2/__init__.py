from fastapi import APIRouter

from .source import router as source_router

router = APIRouter(prefix="/v2")
router.include_router(source_router, tags=["source"])
