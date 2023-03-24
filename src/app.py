import uvicorn
from fastapi import FastAPI, Depends
from api.feed import router as feed_router
from api.article import router as article_router
from api.feedoutlet import router as feedoutlet_router
from api.lib.dependencies import auth

def setup():
    app = FastAPI(title="Bite-sized news", version="0.0.1", dependencies=[Depends(auth)])
    app.include_router(feed_router)
    app.include_router(feedoutlet_router)
    app.include_router(article_router)
    return app


if __name__ == "__main__":
    app = setup()
    uvicorn.run('app:setup', port=5000, reload=True, factory=True)
