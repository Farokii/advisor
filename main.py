from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from routers import users,advisors
from fastapi import FastAPI,Depends,HTTPException
from SQL.database import engine,get_db,Base
from cruds.order_crud import process_expired_orders


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    print("Starting up...")
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

Base.metadata.create_all(bind=engine)

app.include_router(users.router)

app.include_router(advisors.router)

