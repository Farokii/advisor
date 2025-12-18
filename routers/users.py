import dependencies
from schemas import user_schema
from services import user_service
from fastapi import FastAPI,Depends,HTTPException,APIRouter
from SQL.database import engine,get_db,Base
from sqlalchemy.orm import Session
from typing import List
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
#用户端-顾问列表
@router.get("/active-advisors",response_model = List[user_schema.ActiveAdvisors])
async def active_advisors(db: Session = Depends(get_db), current_user_id: int=Depends(dependencies.get_current_user_id)):
    return user_service.active_advisors(db, current_user_id)
#用户端-顾问主页
@router.get("/advisor-profile", response_model=user_schema.AdvisorProfile)
async def get_advisor_profile(
        advisor_id: user_schema.AdvisorID,
        db: Session=Depends(get_db),
        current_usr_id: int=Depends(dependencies.get_current_user_id)
):
    return user_service.get_advisor_profile(db,current_usr_id,advisor_id)
#@router.post("/create-order", response_model=)