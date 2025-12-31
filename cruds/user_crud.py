from fastapi import HTTPException
from models import user_model, advisor_model, review_model
from schemas import user_schema, review_schema
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from security import get_password_hash
from redis_client import redis_client
import json

async def get_user_by_phone(db: AsyncSession, phone: str):
    user = (await db.execute(
        select(user_model.User).where(user_model.User.phone_number == phone)
    )).scalar_one_or_none()
    return user


async def get_user_by_id(db: AsyncSession, user_id: int):
    user = (await db.execute(
        select(user_model.User).where(user_model.User.id == user_id)
    )).scalar_one_or_none()
    return user


async def create_user(db: AsyncSession, user:user_schema.UserCreate):
    #生成哈希密码
    hashed_password = get_password_hash(user.password)
    #创建用户数据库对象
    db_user=user_model.User(
        phone_number=user.phone_number,
        password=hashed_password,
        name=user.name,
        birth=user.birth,
        gender=user.gender,
        bio=user.bio,
        about=user.about,

    )
    #添加到数据库会话（加入购物车）
    db.add(db_user)
    #提交事务，执行数据库操作（结账）
    await db.commit()
    #刷新对象，获取数据库生成的ID（在一步之前db_user中的id,created_at等系统字段还未更新）
    await db.refresh(db_user)
    return db_user


async def update_user_profile(db: AsyncSession, user_id: int, user: user_schema.UserUpdate):
    db_user = (await db.execute(
        select(user_model.User).where(user_model.User.id == user_id)
    )).scalar_one_or_none()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    update_data=user.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_active_advisors(db: AsyncSession):
    active_advisors = ( await db.execute(
        select(advisor_model.Advisor).where(advisor_model.Advisor.service_status == advisor_model.ServiceStatus.in_service)
    ) ).scalars().all()
    return active_advisors


async def get_advisor_profile(db: AsyncSession, advisor_id: int):
    db_advisor = (await db.execute(
        select(advisor_model.Advisor).where(advisor_model.Advisor.id == advisor_id)
    )).scalar_one_or_none()

    if db_advisor is None:
        raise HTTPException(status_code=404, detail="Advisor not found")

    profile = user_schema.AdvisorProfile.model_validate(db_advisor)

    # 计算准时率
    if db_advisor.readings == 0:
        profile.on_time = f"{0}%"
    else: profile.on_time = f"{(db_advisor.completed_readings / db_advisor.readings) * 100:.0f}%"
    # 只取前十条评论
    reviews_raw = await redis_client.zrevrange(f"review:advisor:{db_advisor.id}", 0, 9)
    reviews = []
    for review in reviews_raw:
        try:
            reviews.append(json.loads(review))
        except json.decoder.JSONDecodeError:
            continue
    # 空列表不会被视为None，但会被视为False
    if not reviews:
        reviews = (await db.execute(
            select(review_model.Review).where(review_model.Review.user_id == db_advisor.id).order_by(
                review_model.Review.created_at.desc()).limit(10)
        )).scalars().all()

    review_list = [
        review_schema.AdvisorReviewResponse(
            order_id=review.order_id,
            user_id=review.user_id,
            advisor_id=review.advisor_id,
            user_name=review.user_name,
            order_type=review.order_type,
            rating=review.rating,
            review_text=review.review_text,
            created_at=review.created_at,
        ) for review in reviews
    ]

    return user_schema.AdvisorProfileResponse(
        profile=profile,
        reviews=review_list
    )


async def refund_user_coins(db: AsyncSession, user_id: int, refund_amount: float):
    db_user = (await db.execute(
        select(user_model.User).where(user_model.User.id == user_id)
    )).scalar_one_or_none()

    if db_user is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found when refunding")

    db_user.coin = db_user.coin + refund_amount
    await db.commit()
    await db.refresh(db_user)
    return db_user