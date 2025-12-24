from typing import List
import dependencies
from schemas import advisor_schema, order_schema
from services import advisor_service
from fastapi import FastAPI,Depends,HTTPException,APIRouter
from SQL.database import get_db
from sqlalchemy.orm import Session
from fastapi import HTTPException,status
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
#顾问-订单列表
@router.get("/order-list",response_model = List[order_schema.OrderListResponse])
async def order_list(db: Session = Depends(get_db), current_advisor_id: int = Depends(dependencies.get_current_user_id)):
    advisor_order_list = advisor_service.order_list(db,current_advisor_id)
    if advisor_order_list:
        return advisor_order_list
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No orders found"
            )
# 顾问-订单详情
@router.get("/order-details/{order_id}",response_model=order_schema.OrderDetailsResponse)
async def order_details(order_id: int, db: Session = Depends(get_db), current_advisor_id: int = Depends(dependencies.get_current_user_id)):
    advisor_order_details = advisor_service.order_details(db, current_advisor_id, order_id)
    if advisor_order_details:
        return advisor_order_details
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The order not exists"
        )
# 顾问-回复订单
@router.patch("/complete-order/{order_id}", response_model = advisor_schema.CompleteOrderResponse)
async def complete_order(order_id: int,
                         reply: advisor_schema.Reply,
                         db: Session = Depends(get_db),
                         current_advisor_id: int = Depends(dependencies.get_current_user_id)):
    return advisor_service.complete_order(db, current_advisor_id, order_id, reply)