import dependencies
from schemas import user_schema
from services import user_service
from fastapi import FastAPI,Depends,HTTPException,APIRouter
from SQL.database import engine,get_db,Base
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/users",tags=["users"])
#用户-注册接口
@router.post("/register", response_model=user_schema.UserInDB)
async def register(user: user_schema.UserCreate,db:Session=Depends(get_db)):
    return user_service.register(db,user)

#用户-登录接口
@router.post("/login",response_model=dict)
async def user_login_for_access_token(user_credentials:user_schema.UserLogin,db:Session=Depends(get_db)):
    return user_service.login(db,user_credentials)

#用户-更新个人信息
@router.patch("/profile-edit",response_model=user_schema.UserInDB)
async def user_update_profile(
        user:user_schema.UserUpdate,
        current_user_id: int= Depends(dependencies.get_current_user_id),
        db:Session=Depends(get_db)
):
    return user_service.update_profile(db, current_user_id, user)