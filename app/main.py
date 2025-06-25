
from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.routers import webhook
from app.routers import admin_notification_router
from app.db.database_connection import create_db_and_tables

@asynccontextmanager
async def lifespan(_: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(webhook.router, prefix="/api/v1")
app.include_router(admin_notification_router.router, prefix="/api/v1/admin-notifications")

