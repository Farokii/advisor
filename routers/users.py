import dependencies
from schemas import user_schema, order_schema, review_schema, favorites_schema
from services import user_service
from fastapi import FastAPI,Depends,HTTPException,APIRouter
from SQL.database import engine,get_db,Base
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from fastapi import HTTPException,status
router = APIRouter(prefix="/api/v1/users",tags=["users"])
#用户-注册接口
@router.post("/register", response_model=user_schema.UserInDB)
async def register(user: user_schema.UserCreate, db: AsyncSession=Depends(get_db)):
    return await user_service.register(db,user)

#用户-登录接口
@router.post("/login",response_model=dict)
async def user_login_for_access_token(user_credentials: user_schema.UserLogin, db: AsyncSession = Depends(get_db)):
    return await user_service.login(db,user_credentials)

#用户-更新个人信息
@router.patch("/profile-edit",response_model=user_schema.UserInDB)
async def user_update_profile(
        user: user_schema.UserUpdate,
        current_user_id: int= Depends(dependencies.get_current_user_id),
        db: AsyncSession=Depends(get_db)
):
    return await user_service.update_profile(db, current_user_id, user)
#用户端-顾问列表
@router.get("/active-advisors",response_model = List[user_schema.ActiveAdvisors])
async def active_advisors(db: AsyncSession = Depends(get_db), current_user_id: int=Depends(dependencies.get_current_user_id)):
    return await user_service.active_advisors(db, current_user_id)
#用户端-顾问主页
@router.get("/advisor-profile/{advisor_id}", response_model = user_schema.AdvisorProfileResponse)
async def get_advisor_profile(
        advisor_id: int,
        db: AsyncSession=Depends(get_db),
        current_usr_id: int=Depends(dependencies.get_current_user_id)
):
    return await user_service.get_advisor_profile(db,current_usr_id,advisor_id)
# 用户端-创建订单
@router.post("/create-order", response_model = user_schema.CreateOrderResponse)
async def create_order(
        order: user_schema.CreateOrder,
        db: AsyncSession = Depends(get_db),
        current_user_id: int = Depends(dependencies.get_current_user_id)
):
    return await user_service.create_order(db,current_user_id,order)
#用户端-获取订单列表
@router.get("/order-list", response_model = List[order_schema.OrderListResponse])
async def order_list(db: AsyncSession = Depends(get_db), current_user_id: int = Depends(dependencies.get_current_user_id)):
    user_order_list = await user_service.order_list(db,current_user_id)
    if user_order_list:
        return user_order_list
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No orders found"
            )
#用户端-订单详情
@router.get("/order-details/{order_id}", response_model = order_schema.OrderDetailsResponse)
async def order_details(order_id: int, db: AsyncSession = Depends(get_db), current_user_id: int = Depends(dependencies.get_current_user_id)):
    user_order_details = await user_service.order_details(db, current_user_id, order_id)
    if user_order_details:
        return user_order_details
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The order not exists"
        )

# 用户端-订单评论打赏
@router.post("/review-tip/{order_id}", response_model = dict)
async def review_tip(order_id: int,
                    review: review_schema.ReviewInfo,
                    db: AsyncSession = Depends(get_db),
                    current_user_id: int = Depends(dependencies.get_current_user_id)):
    return await user_service.review_tip(order_id, review,db, current_user_id)
# 用户端-流水信息
@router.get("/coin-trans", response_model = List[order_schema.CoinTransResponse] )
async def coin_trans(current_user_id: int = Depends(dependencies.get_current_user_id)):
    return await user_service.coin_trans(current_user_id)
# 用户端-收藏顾问
@router.post("/save-advisor/{advisor_id}", response_model = favorites_schema.SaveAdvisorResponse)
async def save_advisor(advisor_id: int, db: AsyncSession = Depends(get_db), current_user_id: int = Depends(dependencies.get_current_user_id)):
    return await user_service.save_advisor(db, current_user_id, advisor_id)
# 用户端-取消收藏顾问
@router.delete("/unsave-advisor/{advisor_id}", response_model = dict)
async def unsave_advisor(advisor_id: int, db: AsyncSession = Depends(get_db), current_user_id: int = Depends(dependencies.get_current_user_id)):
    return await user_service.unsave_advisor(db, current_user_id, advisor_id)
# 用户端-收藏列表
@router.get("/favorites-list", response_model = List[favorites_schema.SaveAdvisorResponse])
async def favorites_list(db: AsyncSession = Depends(get_db), current_user_id: int = Depends(dependencies.get_current_user_id)):
    return await user_service.favorites_list(db, current_user_id)