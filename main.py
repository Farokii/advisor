from pip._internal.network import auth

from routers import users,advisors
from fastapi import FastAPI,Depends,HTTPException
from SQL.database import engine,get_db,Base
app = FastAPI(version="1.0.0")

Base.metadata.create_all(bind=engine)

app.include_router(users.router)

app.include_router(advisors.router)