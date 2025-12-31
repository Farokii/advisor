from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from routers import users,advisors
from fastapi import FastAPI,Depends,HTTPException
from SQL.database import engine,get_db,Base
from cruds.order_crud import process_expired_orders
from config import Settings
import os

# 在mysql数据库建表
async def create_tables():
    """异步创建所有表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    print("Development Mode Starting up...")
    await create_tables()  # 创建数据库表
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        func=process_expired_orders,
        trigger=IntervalTrigger(seconds=60),
        id="process_expired_orders",
        name="process_expired_orders",
        replace_existing=True,
    )
    scheduler.start()
    print("Scheduler started.")
    app_instance.state.scheduler = scheduler
    yield

    print("shutting down...")
    scheduler.shutdown()
    print("Scheduler shut down.")

app = FastAPI(version="1.0.0", lifespan=lifespan)


app.include_router(users.router)

app.include_router(advisors.router)

