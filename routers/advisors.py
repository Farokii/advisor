from fastapi.temp_pydantic_v1_params import Body

import dependencies
from schemas import advisor_schema
from services import advisor_service
from fastapi import FastAPI,Depends,HTTPException,APIRouter
from SQL.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/advisors",tags=["advisors"])
#顾问-注册接口
@router.post("/register", response_model=advisor_schema.AdvisorCreateResponse)
async def register(advisor: advisor_schema.AdvisorCreate,db:Session=Depends(get_db)):
    return advisor_service.register(db,advisor)
#顾问-登录接口
@router.post("/login",response_model=dict)
async def login(advisor: advisor_schema.AdvisorLogin,db:Session=Depends(get_db)):
    return advisor_service.login(db,advisor)
#顾问-信息修改
@router.patch("/profile-edit",response_model=advisor_schema.AdvisorUpdateProfileResponse)
async def update_profile(
        advisor: advisor_schema.AdvisorUpdateProfile,
        db:Session= Depends(get_db),
        current_advisor_id: int= Depends(dependencies.get_current_user_id)
):
    return advisor_service.update_profile(db,advisor,current_advisor_id)
#顾问-个人主页
@router.get("/profile",response_model=advisor_schema.ProfileResponse)
async def profile(db: Session = Depends(get_db), current_advisor_id: int = Depends(dependencies.get_current_user_id)):
    return advisor_service.profile(db,current_advisor_id)
#顾问-接单状态更新
@router.patch("/work-status",response_model=advisor_schema.UpdateWorkStatusResponse)
async def work_status(
        advisor: advisor_schema.UpdateWorkStatus,
        db: Session = Depends(get_db),
        current_advisor_id: int = Depends(dependencies.get_current_user_id)
):
    return advisor_service.update_work_status(db,current_advisor_id,advisor)
#顾问-服务状态更新
@router.patch("/service-status", response_model = advisor_schema.UpdateServiceStatusResponse)
async def service_status(
        advisor: advisor_schema.UpdateServiceStatus,
        db: Session = Depends(get_db),
        current_advisor_id: int = Depends(dependencies.get_current_user_id)
):
    return advisor_service.update_service_status(db,current_advisor_id,advisor)
#顾问-价格修改
@router.patch("/price",response_model=advisor_schema.UpdatePriceResponse)
async def price(
        advisor: advisor_schema.UpdatePrice,
        db: Session = Depends(get_db),
        current_advisor_id: int = Depends(dependencies.get_current_user_id)
):
    return advisor_service.update_price(db,current_advisor_id,advisor)