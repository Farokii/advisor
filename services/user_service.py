#处理业务逻辑，与数据库操作解耦
from datetime import timedelta

from sqlalchemy.util import await_only

from config import Settings
import security
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException,status
from schemas import user_schema, review_schema, order_schema
from cruds import user_crud, advisor_crud, order_crud, review_crud, favorites_crud
from models.order_model import OrderType, OrderStatus
from coin_trans import get_coin_trans
settings = Settings()

#1.用户端-注册
async def register(db: AsyncSession, user: user_schema.UserCreate):
    #检查手机号是否已注册
    db_user=await user_crud.get_user_by_phone(db, phone=user.phone_number)
    if db_user:
        raise HTTPException(status_code=400, detail="Phone already registered")
    return await user_crud.create_user(db,user)

#2.用户端-登录
async def login(db: AsyncSession, user: user_schema.UserLogin):
    # 通过手机号验证登录用户是否存在
    db_user = await user_crud.get_user_by_phone(db, user.phone_number)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",  # 不要透露是手机号泄漏了还是密码错了，方式信息泄漏
            headers={"WWW-Authenticate": "Bearer"}
        )
    # 验证密码是否正确
    if not security.verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    #账号密码匹配成功，生成token
    #定义令牌过期时间
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    #创建令牌
    access_token = security.create_access_token(
        data={"sub": str(db_user.id)},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token , "token_type":"bearer"}

#3.用户端-更新个人信息
async def update_profile(db: AsyncSession, user_id: int, user: user_schema.UserUpdate):
    updated_user=await user_crud.update_user_profile(db,user_id,user)
    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user profile",
        )
    return updated_user

#4.用户端-顾问列表
async def active_advisors(db: AsyncSession, user_id: int):
    return await user_crud.get_active_advisors(db)

#5.用户端-顾问主页
async def get_advisor_profile(db: AsyncSession, user_id: int, advisor_id: int):
    return await user_crud.get_advisor_profile(db, advisor_id)

#6.用户端-创建订单
async def create_order(db: AsyncSession, user_id :int, order: user_schema.CreateOrder):
    db_user = await user_crud.get_user_by_id(db, user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    db_advisor = await advisor_crud.get_advisor_by_id(db, order.advisor_id)
    #判断订单顾问是否存在
    if db_advisor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Advisor not found",
        )
    # 判断订单顾问是否处于适合接单状态
    if db_advisor.service_status == "out_of_service" or db_advisor.work_status == "busy":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The advisor is not accepting order now",
        )
    # 判断顾问是否只接受加急订单，以及用户订单是否加急
    if db_advisor.work_status == "urgent_only" and order.is_urgent != True:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The advisor only accepts urgent order",
        )
    # 判断用户订单类型是否合法
    if order.order_type not in OrderType:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid order type: {order.order_type}",
        )
    # 判断顾问是否接受该类型订单
    if getattr(db_advisor, f"accept_{order.order_type.value}") is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The advisor doesn't accept {order.order_type} order",
        )
    # 判断用户目前持有金币是否足够支付订单
    price = getattr(db_advisor, f"price_{order.order_type.value}")
    if order.is_urgent : price += price * 0.5 # 加急订单涨价一半
    if db_user.coin < price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The user is unable to pay for this order",
        )

    new_order = await order_crud.create_order(db, user_id, order, price)
    return new_order


async def order_list(db: AsyncSession, user_id : int):
    return await order_crud.user_order_list(db, user_id)

async def order_details(db: AsyncSession, user_id: int, order_id: int):
    order = await order_crud.get_order_by_id(db, order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    if order.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The user {user_id} is not allowed to see order {order_id} details",
        )
    return await order_crud.get_order_details(db, order_id)


async def review_tip(order_id: int, review: review_schema.ReviewInfo, db: AsyncSession, user_id : int):
    db_order = await order_crud.get_order_by_id(db, order_id)
    if db_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    if db_order.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The user {user_id} is not allowed to review or tip order {order_id}",
        )
    if db_order.order_status == OrderStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The order {order_id} is pending and can't be reviewed now",
        )
    return await review_crud.review_tip(db, order_id, review, user_id)


async def save_advisor(db: AsyncSession, user_id: int, advisor_id: int):
    return await favorites_crud.save_advisor(db, user_id, advisor_id)


async def unsave_advisor(db: AsyncSession, user_id: int, advisor_id: int):
    return await favorites_crud.unsave_advisor(db, user_id, advisor_id)


async def favorites_list(db: AsyncSession, user_id: int):
    return await favorites_crud.favorites_list(db, user_id)

async def coin_trans(user_id: int):
    logs = await get_coin_trans("user", user_id)
    return [
        order_schema.CoinTransResponse(
            type=log.get("type"),
            credit=log.get("credit"),
            time=log.get("time"),
        )for log in logs
    ]