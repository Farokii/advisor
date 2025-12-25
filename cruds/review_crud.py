from models import order_model, user_model, advisor_model, review_model
from schemas import user_schema, advisor_schema, order_schema, review_schema
from sqlalchemy.orm import Session, joinedload
from redis_client import redis_client
from config import Settings
from fastapi import HTTPException, status
from coin_trans import add_coin_trans
import time

settings = Settings()
def review_tip(db: Session, order_id: int, review: review_schema.ReviewInfo, user_id: int):
    db_user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    db_order = db.query(order_model.Order).filter(order_model.Order.id == order_id).options(joinedload(order_model.Order.advisor)).first()
    db_advisor = db.query(advisor_model.Advisor).filter(advisor_model.Advisor.id == db_order.advisor_id).first()
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
    add_coin_trans("user", user_id, "Tip", f"-{review.tip}")
    #  更改顾问数据
    db_advisor.ratings = (db_advisor.ratings * db_advisor.review_count + review.rating) / (db_advisor.review_count + 1)
    db_advisor.review_count = db_advisor.review_count + 1
    db_advisor.coin += review.tip
    add_coin_trans("advisor", db_advisor.id, "Tip", f"+{review.tip}")

    db.commit()
    db.refresh(db_user)
    db.refresh(db_advisor)
    db.refresh(db_review)
    # redis存评论详情 用户本人查看时能看到tip,存到顾问评论表中没有tip
    now_time = int(time.time())
    review_details = review_schema.AdvisorReviewResponse(
        order_id=db_review.order_id,
        user_id=db_review.user_id,
        advisor_id=db_review.id,
        user_name=db_review.user_name,
        order_type=db_review.order_type,
        rating=db_review.rating,
        review_text=db_review.review_text,
        created_at=db_review.created_at,
    )
    redis_client.zadd(f"review:advisor:{db_advisor}", {review_details.model_dump_json(): now_time})

    return {"id": db_review.id, "review_tip": "success"}
