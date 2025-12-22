from models import user_model,advisor_model,order_model
from schemas import user_schema, advisor_schema
from sqlalchemy.orm import Session
from redis_client import redis_client
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
    db.commit()
    db.refresh(db_order)
    ttl_final = int(1 * 1 * 60)
    ttl_urgent = int(1 * 30 )
    try:
        redis_client.setex(f"order:expire:normal:{db_order.id}", ttl_final, "")
        print(f"[Order Created] Set Redis key 'order:expire:normal:{db_order.id}' with ttl {ttl_final}s for order ID {db_order.id}")
        if db_order.is_urgent:
            redis_client.setex(f"order:expire:urgent:{db_order.id}", ttl_urgent, "")
            print(f"[Order Created] Set Redis key 'order:expire:urgent:{db_order.id}' with ttl {ttl_urgent}s for order ID {db_order.id}")
    except Exception as e:
        print(f"[Redis Error] Failed to set expire time for order ID {db_order.id}: {e}")
    return db_order
