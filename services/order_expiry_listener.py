import redis
import threading
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import order_model, advisor_model, order_model
from config import Settings
from cruds import order_crud, user_crud
settings = Settings()

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_pubsub_client():
    return redis.Redis.from_url(settings.REDIS_URL, decode_responses=True).pubsub()


def handle_urgent_downgrade(order_id: int):
    db = SessionLocal()
    try:
        # 只处理状态仍是 pending 的加急订单
        order = db.query(order_model.Order).filter(
            order_model.Order.id == order_id,
            order_model.Order.order_status == order_model.OrderStatus.pending,
            order_model.Order.is_urgent == True
        ).first()

        if not order:
            print(f"[Urgent] Order {order_id} not found or already processed")
            return

        # 退还多付的 0.5 倍金币
        refund_amount = order.current_price * (1 / 3)  # 因为 1.5x 中多付了 0.5x，占总价 1/3
        user_crud.refund_user_coins(db, order.user_id, refund_amount)

        # 降级为普通订单（标记 is_urgent=False，但保留 pending 状态）
        order.current_price = order.current_price * (2 / 3)
        order.is_urgent = False
        db.commit()
        print(f"[Urgent] Downgraded order {order_id} to normal order, refunded {refund_amount} gold to user {order.user_id}")

    except Exception as e:
        db.rollback()
        print(f"[Urgent] Error downgrading {order_id}: {e}")
    finally:
        db.close()


def listen_for_urgent_order_expiry():
    """监听加急订单过期 (Key: order:expire:urgent:{id})"""
    print("🔴 Starting urgent order expiry listener...")
    pubsub = get_pubsub_client()
    pubsub.psubscribe('__keyevent@0__:expired')

    for message in pubsub.listen():
        if message['type'] == 'pmessage':
            key = message['data']
            if key.startswith("order:expire:urgent:"):
                try:
                    order_id = int(key.split(":")[-1])
                    handle_urgent_downgrade(order_id)
                except (ValueError, IndexError) as e:
                    print(f"[URGENT] Parse error: {e}")


def handle_final_expiry(order_id: int):
    db = SessionLocal()
    try:
        order = db.query(order_model.Order).filter(
            order_model.Order.id == order_id,
            order_model.Order.order_status == order_model.OrderStatus.pending
        ).first()

        if not order:
            return

        # 退还剩余金币（如果是加急且已降级，则退 1.0x；如果是普通，也退 1.0x）
        # 注意：加急订单在降级时已退 0.5x，这里退剩下的 1.0x
        refund_amount = order.current_price * (2 / 3) if order.is_urgent else order.current_price
        user_crud.refund_user_coins(db, order.user_id, refund_amount)

        # 标记为 expired
        order.order_status = order_model.OrderStatus.expired
        db.commit()
        print(f"[Final] Expired order {order_id}, refunded {refund_amount} gold to user {order.user_id}")

    except Exception as e:
        db.rollback()
        print(f"[Final] Error expiring {order_id}: {e}")
    finally:
        db.close()


def listen_for_normal_order_expiry():
    """监听普通订单过期 (Key: order:expire:normal:{id})"""
    print("🟢 Starting normal order expiry listener...")
    pubsub = get_pubsub_client()
    pubsub.psubscribe('__keyevent@0__:expired')

    for message in pubsub.listen():
        if message['type'] == 'pmessage':
            key = message['data']
            if key.startswith("order:expire:normal:"):
                try:
                    order_id = int(key.split(":")[-1])
                    handle_final_expiry(order_id)
                except (ValueError, IndexError) as e:
                    print(f"[NORMAL] Parse error: {e}")


if __name__ == "__main__":
    # 创建两个线程，分别运行两个监听器
    t1 = threading.Thread(target=listen_for_normal_order_expiry, daemon=True)
    t2 = threading.Thread(target=listen_for_urgent_order_expiry, daemon=True)

    t1.start()
    t2.start()

    try:
        t1.join()
        t2.join()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down listeners...")