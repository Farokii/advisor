from fastapi import HTTPException

from models import user_model,advisor_model,order_model, review_model
from schemas import user_schema, advisor_schema, review_schema
from sqlalchemy.orm import Session
from security import get_password_hash,verify_password
from redis_client import redis_client
import json

def get_user_by_phone(db:Session,phone:str):
    return db.query(user_model.User).filter(user_model.User.phone_number==phone).first()
def get_user_by_id(db:Session,user_id:int):
    return db.query(user_model.User).filter(user_model.User.id == user_id).first()

def create_user(db:Session,user:user_schema.UserCreate):
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
    db.commit()
    #刷新对象，获取数据库生成的ID（在一步之前db_user中的id,created_at等系统字段还未更新）
    db.refresh(db_user)
    return db_user

def update_user_profile(db:Session,user_id:int,user:user_schema.UserUpdate):
    db_user=db.query(user_model.User).filter(user_model.User.id == user_id).first()
    if db_user is None:
        return None

    update_data=user.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user

def get_active_advisors(db:Session,user_id:int):
    active_advisors=db.query(advisor_model.Advisor).filter(
        advisor_model.Advisor.service_status == advisor_model.ServiceStatus.in_service).all()
    return active_advisors

def get_advisor_profile(db: Session, advisor_id: int):
    db_advisor = db.query(advisor_model.Advisor).filter(advisor_model.Advisor.id == advisor_id).first()
    profile = user_schema.AdvisorProfile.model_validate(db_advisor)
    if db_advisor is None:
        raise HTTPException(status_code=404, detail="Advisor not found")
    # 计算准时率
    if db_advisor.readings == 0:
        profile.on_time = f"{0}%"
    else: profile.on_time = f"{(db_advisor.completed_readings / db_advisor.readings) * 100:.0f}%"
    # 只取前十条评论
    reviews_raw = redis_client.zrevrange(f"review:advisor:{db_advisor.id}", 0, 9)
    reviews = []
    for review in reviews_raw:
        try:
            reviews.append(json.loads(review))
        except json.decoder.JSONDecodeError:
            continue
    # 空列表不会被视为None，但会被视为False
    if not reviews:
       reviews = db.query(review_model.Review).filter(
           review_model.Review.advisor_id == db_advisor.id).order_by(
           review_model.Review.created_at.desc()).limit(10).all()
    print(len(reviews))
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


def refund_user_coins(db: Session, user_id: int, refund_amount: float):
    db_user=db.query(user_model.User).filter(user_model.User.id == user_id).first()
    if db_user is None:
        return None
    db_user.coin = db_user.coin + refund_amount
    db.commit()
    db.refresh(db_user)
    return db_user