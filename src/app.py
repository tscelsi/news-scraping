from contextlib import asynccontextmanager

import uvicorn
from fastapi import APIRouter, Depends, FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

# from api.article import router as article_router
# from api.feed import router as feed_router
# from api.feedoutlet import router as feedoutlet_router
from api.lib.dependencies import on_auth

# from api.source import router as source_router
from api.v2.source import router as source_router

v2_router = APIRouter(prefix="/v2", tags=["v2"])
v2_router.include_router(source_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    FastAPICache.init(backend=InMemoryBackend())
    yield


def setup():
    app = FastAPI(
        title="Bite-sized news",
        version="0.0.1",
        # dependencies=[Depends(on_auth)],
        lifespan=lifespan,
    )
    # app.include_router(feed_router)
    # app.include_router(feedoutlet_router)
    # app.include_router(article_router)
    # app.include_router(source_router)
    app.include_router(v2_router)
    return app


if __name__ == "__main__":
    app = setup()
    uvicorn.run("app:setup", port=5000, reload=True, factory=True)
