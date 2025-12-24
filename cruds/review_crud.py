from sqlalchemy.sql.functions import now

from models import order_model, user_model, advisor_model, review_model
from models.review_model import Review
from schemas import user_schema, advisor_schema, order_schema, review_schema
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from redis_client import redis_client
from config import Settings
from datetime import datetime, timedelta
from cruds import advisor_crud, user_crud
from SQL.database import SessionLocal
from fastapi import HTTPException, status
from coin_trans import add_coin_trans
import json
import time

settings = Settings()
def review_tip(db: Session, order_id: int, review: review_schema.ReviewInfo, user_id: int):
    db_user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    db_order = db.query(order_model.Order).filter(order_model.Order.id == order_id).options(joinedload(order_model.Order.advisor)).first()
    if db_user.coin < review.tip:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"The user {user_id} don't have enough coins to tip",
        )
    # 创建评论
    db_review = review_model.Review(
        order_id=order_id,
        user_id=user_id,
        advisor_id=db_order.advisor.id,
        user_name=db_user.name,
        order_type=db_order.order_type,
        rating=review.rating,
        review_text=review.review_text,
        tip=review.tip,
    )
    db.add(db_review)
    # 更改用户数据
    db_user.coin -= review.tip
    add_coin_trans(user_id, "Tip", f"-review.tip")
    #  更改顾问数据
    db_advisor = db.query(advisor_model.Advisor).filter(advisor_model.Advisor.id == db_order.advisor_id).first()
    db_advisor.rating = (db_advisor.rating * db_advisor.review_count + review.rating) / (db_advisor.review_count + 1)
    db_advisor.review_count = db_advisor.review_count + 1
    if review.tip > 0:
        db_advisor.coin += review.tip

    db.commit()
    db.refresh(db_user)
    db.refresh(db_advisor)
    db.refresh(db_review)

    now_time = int(time.time())
    review_details = review_schema.ReviewTipResponse.model_validate(db_review)
    redis_client.zadd(f"review:advisor:{db_advisor.id}", {json.dumps(review_details.model_dump_json()): now_time})

    return {"id": db_review.id, review_tip: "success"}
