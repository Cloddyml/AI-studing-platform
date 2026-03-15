from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import engine
from app.utils.qwen_client import close_http_client, init_http_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_http_client()
    yield
    await close_http_client()
    await engine.dispose()
