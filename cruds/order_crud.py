from models import order_model, user_model, advisor_model
from schemas import user_schema, advisor_schema, order_schema
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from redis_client import redis_client
from config import Settings
from datetime import datetime, timedelta, timezone
from cruds import advisor_crud, user_crud
from SQL.database import SessionLocal
from coin_trans import add_coin_trans
import json
settings = Settings()

def get_order_by_id(db: Session, order_id: int):
    order = db.query(order_model.Order).filter(order_model.Order.id == order_id).first()
    return order

def create_order(db: Session, user_id: int, order: user_schema.CreateOrder, price: float):
    db_order=order_model.Order(
        user_id=user_id,
        advisor_id=order.advisor_id,
        general_situation=order.general_situation,
        specific_question=order.specific_question,
        is_urgent=order.is_urgent,
        order_type=order.order_type,
        current_price=price,
    )
    db.add(db_order)
    #扣除用户金币
    db_user = db.query(user_model.User).filter(user_model.User.id == user_id).first()
    db_user.coin -= price

    #增加顾问订单数
    db_advisor = db.query(advisor_model.Advisor).filter(advisor_model.Advisor.id == order.advisor_id).first()
    db_advisor.readings += 1

    db.commit()
    db.refresh(db_order)

    # 添加用户流水信息
    if db_order.is_urgent:
        add_coin_trans("user", user_id, "Speed Up Order", f"-{price * 1/3}")
        add_coin_trans("user", user_id, f"{db_order.order_type.value}", f"-{price * 2/3}")
    else: add_coin_trans("user", user_id, f"{db_order.order_type.value}", f"-{price}")
    """
    ttl_final = settings.URGENT_EXPIRE_MINUTES * 60
    ttl_urgent = settings.URGENT_EXPIRE_MINUTES * 60
    try:
        redis_client.setex(f"order:expire:normal:{db_order.id}", ttl_final, "")
        print(f"[Order Created] Set Redis key 'order:expire:normal:{db_order.id}' with ttl {ttl_final}s for order ID {db_order.id}")
        if db_order.is_urgent:
            redis_client.setex(f"order:expire:urgent:{db_order.id}", ttl_urgent, "")
            print(f"[Order Created] Set Redis key 'order:expire:urgent:{db_order.id}' with ttl {ttl_urgent}s for order ID {db_order.id}")
    except Exception as e:
        print(f"[Redis Error] Failed to set expire time for order ID {db_order.id}: {e}")
    """
    return db_order

def process_expired_orders():
    db = SessionLocal()
    """
    定时任务：处理过期订单（包括加急订单的第一阶段过期和普通/最终过期）
    """
    now = datetime.now(timezone.utc).replace(tzinfo=None) # UTC时间，与数据库时间一致

    # 加急订单过期处理
    expiry_urgent_time = now - timedelta(minutes=settings.URGENT_EXPIRE_MINUTES)
    expired_urgent_orders = db.query(order_model.Order).filter(
        and_(
            order_model.Order.is_urgent == True,
            order_model.Order.order_status == order_model.OrderStatus.pending,
            order_model.Order.created_at < expiry_urgent_time
        )
    ).all()

    for order in expired_urgent_orders:
        try:
            # 计算加急费
            urgent_fee = order.current_price / 3

            # 1. 退款加急费
            user_crud.refund_user_coins(
                db=db,
                user_id=order.user_id,
                refund_amount=urgent_fee,
            )
            add_coin_trans("user", order.user_id, "Speed-up Expired Refund", f"+{urgent_fee}")
            # 2. 更新订单状态 (标记加急费已退，订单转为普通)
            order.is_urgent = False
            order.current_price -= urgent_fee
            # 订单状态仍为 'pending'，等待24小时最终过期

            # 删除缓存信息，下次查看时会重新查询数据库并生成新缓存
            cache_key = f"order:details:{order.id}"
            cache_value = redis_client.get(cache_key)
            if cache_value:
                redis_client.delete(cache_key)

            print(f"Downgrade urgent order {order.id} to normal, refunded {urgent_fee} coins to {order.user_id}.")

        except Exception as e:
            # 如果处理单个订单失败，记录错误并回滚，但不影响其他订单
            print(f"Error processing urgent order {order.id}: {e}")
            db.rollback()
            # 重新查询该订单以确保状态未被部分更新
            db.refresh(order)
            continue # 继续处理下一个

    # 处理普通过期订单
    expiry_normal_time = now - timedelta(minutes=settings.NORMAL_EXPIRE_MINUTES)
    expired_normal_orders = db.query(order_model.Order).filter(
        and_(
            order_model.Order.order_status == order_model.OrderStatus.pending,
            order_model.Order.created_at < expiry_normal_time,
        )
    ).all()

    for order in expired_normal_orders:
        try:
            # 3. 退款全款 (或剩余款项，如果已退加急费)
            refund_amount = order.current_price

            user_crud.refund_user_coins(
                db=db,
                user_id=order.user_id,
                refund_amount=refund_amount,
            )
            add_coin_trans("user", order.user_id,f"{order.order_type.value} Expired Refund", f"+{refund_amount}")
            # 4. 更新订单状态为过期
            order.order_status = order_model.OrderStatus.expired
            order.current_price = 0.0
            order.is_urgent = False
            order.final_amount = 0.0

            # 删除缓存信息，下次查看时会重新查询数据库并生成新缓存
            cache_key = f"order:details:{order.id}"
            cache_value = redis_client.get(cache_key)
            if cache_value:
                redis_client.delete(cache_key)

            print(f"Normal expired order {order.id} is refunded, refund {refund_amount} coins to {order.user_id}.")

        except Exception as e:
            print(f"Error processing normal expired order {order.id}: {e}")
            db.rollback()
            db.refresh(order)
            continue # 继续处理下一个

    # --- 5. 提交所有更改 ---
    try:
        db.commit()
        print("Expired orders processing completed successfully.")
    except Exception as e:
        print(f"Failed to commit changes during order expiry processing: {e}")
        db.rollback() # 如果提交失败，回滚所有更改
    finally:
        db.close()

    return


def advisor_order_list(db: Session, advisor_id: int):
    orders = db.query(order_model.Order).filter(
        order_model.Order.advisor_id == advisor_id).options(
        joinedload(order_model.Order.user)).all()
    order_list = []

    for order in orders:
        advisor_order = order_schema.OrderListResponse(
            order_id=order.id,
            related_id=order.user_id,
            name=order.user.name,
            order_type=order.order_type,
            order_status=order.order_status,
            specific_question=order.specific_question,
            is_urgent=order.is_urgent,
            created_at=order.created_at
        )
        order_list.append(advisor_order)
    return order_list


def user_order_list(db: Session, user_id: int):
    orders = db.query(order_model.Order).filter(
        order_model.Order.user_id == user_id).options(
        joinedload(order_model.Order.advisor)).all()
    order_list = []

    for order in orders:
        advisor_order = order_schema.OrderListResponse(
            order_id=order.id,
            related_id=order.advisor_id,
            name=order.advisor.name,
            order_type=order.order_type,
            order_status=order.order_status,
            specific_question=order.specific_question,
            is_urgent=order.is_urgent,
            created_at=order.created_at
        )
        order_list.append(advisor_order)
    return order_list


def get_order_details(db: Session, order_id):
    cache_key = f"order:details:{order_id}"
    cache_value = redis_client.get(cache_key)
    if cache_value:
        # 从缓存反序列化为pydantic模型
        return order_schema.OrderDetailsResponse(**json.loads(cache_value))
    # redis缓存中没有发对应订单详情
    order = db.query(order_model.Order).filter(order_model.Order.id == order_id).options(
        joinedload(order_model.Order.user),
        joinedload(order_model.Order.advisor),
    ).first()
    order_details = order_schema.OrderDetailsResponse(
        order_id=order.id,
        user_id=order.user_id,
        user_name=order.user.name,
        birth=order.user.birth,
        gender=order.user.gender,
        advisor_id=order.advisor_id,
        advisor_name=order.advisor.name,
        order_status=order.order_status,
        order_type=order.order_type,
        is_urgent=order.is_urgent,
        general_situation=order.general_situation,
        specific_question=order.specific_question,
        reply=order.reply,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


    redis_client.setex(cache_key, settings.ORDER_DETAILS_EXPIRE_MINUTES, order_details.model_dump_json())

    return order_details

# 回复订单
def complete_order(db: Session, order_id: int, advisor_id: int, reply: advisor_schema.Reply):
    order = get_order_by_id(db, order_id)
    # 更新订单信息
    order.reply = reply.reply
    order.order_status = order_model.OrderStatus.completed
    order.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
    order.is_urgent = False
    order.final_amount = order.current_price
    # 更新顾问信息
    advisor = advisor_crud.get_advisor_by_id(db, advisor_id)
    advisor.coin += order.final_amount
    add_coin_trans("advisor", advisor_id, f"{order.order_type.value}", f"+{order.final_amount}")
    advisor.completed_readings += 1
    db.commit()
    db.refresh(order)
    db.refresh(advisor)

    # 删除缓存信息，下次查看时会重新查询数据库并生成新缓存
    cache_key = f"order:details:{order_id}"
    cache_value = redis_client.get(cache_key)
    if cache_value:
        redis_client.delete(cache_key)


    return advisor_schema.CompleteOrderResponse(
        order_id=order.id,
        completed_at=order.completed_at,
        profit=order.final_amount
    )