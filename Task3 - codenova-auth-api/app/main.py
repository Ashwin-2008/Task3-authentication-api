
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.database.init_db import init_db
from app.routers import auth, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Authentication API",
    lifespan=lifespan,
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")


@app.get("/api/v1/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}
