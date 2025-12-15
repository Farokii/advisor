from fastapi import FastAPI
from SQL.database import engine
from SQL.database import Base

app = FastAPI()
Base.metadata.create_all(bind=engine)
