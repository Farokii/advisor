from models import review_model
from schemas import review_schema
from sqlalchemy.ext.asyncio import AsyncSession
from redis_client import redis_client
from config import Settings
from fastapi import HTTPException, status
from coin_trans import add_coin_trans
from cruds import user_crud, advisor_crud, order_crud
import time

settings = Settings()

async def review_tip(db: AsyncSession, order_id: int, review: review_schema.ReviewInfo, user_id: int):
    db_user = await user_crud.get_user_by_id(db, user_id)
    db_advisor = await advisor_crud.get_advisor_by_id(db, user_id)
    db_order = await order_crud.get_order_by_id(db, order_id)

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
    await add_coin_trans("user", user_id, "Tip", f"-{review.tip}")
    #  更改顾问数据
    db_advisor.ratings = (db_advisor.ratings * db_advisor.review_count + review.rating) / (db_advisor.review_count + 1)
    db_advisor.review_count = db_advisor.review_count + 1
    db_advisor.coin += review.tip
    await add_coin_trans("advisor", db_advisor.id, "Tip", f"+{review.tip}")

    await db.commit()
    await db.refresh(db_user)
    await db.refresh(db_advisor)
    await db.refresh(db_review)
    # redis存评论详情 用户本人查看时能看到tip,存到顾问评论表中没有tip
    now_time = int(time.time())
    review_details = review_schema.AdvisorReviewResponse.model_validate(db_review)
    await redis_client.zadd(f"review:advisor:{db_advisor}", {review_details.model_dump_json(): now_time})

    return {"id": db_review.id, "review_tip": "success"}
