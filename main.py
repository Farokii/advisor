from starlette import status
import dependencies
from models import user_model
from schemas import user_schema
from services import user_service
from fastapi import FastAPI,Depends,HTTPException
from SQL.database import engine,get_db,Base
from sqlalchemy.orm import Session
app = FastAPI(version="1.0.0")

Base.metadata.create_all(bind=engine)
#用户-注册接口
@app.post("/api/v1/users/register", response_model=user_schema.UserInDB)
async def register(user: user_schema.UserCreate,db:Session=Depends(get_db)):
    return user_service.register_user(db,user)

#用户-登录接口
@app.post("/api/v1/users/login",response_model=dict)
async def user_login_for_access_token(user_credentials:user_schema.UserLogin,db:Session=Depends(get_db)):
    return user_service.login_user(db,user_credentials)

#用户-更新个人信息
@app.patch("/api/v1/users/me",response_model=user_schema.UserInDB)
async def user_update_profile(
        user:user_schema.UserUpdate,
        current_user_id:int=Depends(dependencies.get_current_user_id),
        db:Session=Depends(get_db)
):
    return user_service.update_user_profile(db, current_user_id, user)


