
from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.routers import webhook
from app.db.database_connection import create_db_and_tables

@asynccontextmanager
async def lifespan(_: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(webhook.router, prefix="/api/v1")

